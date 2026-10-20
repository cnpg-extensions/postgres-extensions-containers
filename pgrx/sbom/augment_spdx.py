"""CNPG hook API v1. Uses the generator image's Syft for a local Cargo.lock scan; no network access.

Cargo relationships describe the configured target source graph, not surviving
linked symbols. Build/dev dependencies and proc-macro-only crates are excluded.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import quote

NAMESPACE = 'https://github.com/cnpg-extensions/postgres-extensions-containers/pgrx-enrichment/v1'
TARGETS = {'linux/amd64': ('x86_64-unknown-linux-gnu', 62), 'linux/arm64': ('aarch64-unknown-linux-gnu', 183)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result


def parse_json(data):
    try:
        result = json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as error:
        raise ValueError(f'invalid evidence JSON: {error}') from error
    require(isinstance(result, dict), 'expected JSON object')
    return result


def safe_file(root, relative):
    require(isinstance(relative, str) and relative, 'missing relative path')
    path = PurePosixPath(relative)
    require(not path.is_absolute() and '..' not in path.parts and str(path) == relative,
            f'unsafe evidence path: {relative}')
    current = Path(root)
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), f'symlink in evidence path: {relative}')
    require(current.is_file(), f'missing regular evidence file: {relative}')
    return current


def checked_bytes(root, relative, expected):
    require(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected), 'invalid SHA256')
    data = safe_file(root, relative).read_bytes()
    require(sha256(data) == expected, f'hash mismatch: {relative}')
    return data


def indexed(items, key):
    result = {}
    for item in items:
        identity = item[key]
        require(identity not in result, f'duplicate identity: {identity}')
        result[identity] = item
    return result


def target_matches(condition, facts, triple):
    if condition is None:
        return True
    require(facts is not None and triple, 'target configuration is required')
    if not condition.startswith('cfg('):
        return condition == triple
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z_0-9]*|[(),=]', condition)
    require(''.join(tokens) == re.sub(r'\s+', '', condition), 'invalid target condition')
    position = 0

    def expression():
        nonlocal position
        require(position < len(tokens), 'truncated target condition')
        name = tokens[position]; position += 1
        if position < len(tokens) and tokens[position] == '(':
            require(name in ('cfg', 'all', 'any', 'not'), 'unknown target condition operator')
            position += 1; children = []
            while position < len(tokens) and tokens[position] != ')':
                children.append(expression())
                if position < len(tokens) and tokens[position] == ',':
                    position += 1
                else:
                    break
            require(position < len(tokens) and tokens[position] == ')', 'unclosed target condition')
            position += 1
            if name in ('cfg', 'not'):
                require(len(children) == 1, 'invalid unary target condition')
                return children[0] if name == 'cfg' else not children[0]
            return all(children) if name == 'all' else any(children)
        if position < len(tokens) and tokens[position] == '=':
            position += 1
            require(position < len(tokens) and tokens[position].startswith('"'), 'invalid target value')
            name += '=' + tokens[position]; position += 1
        return name in facts

    result = expression()
    require(position == len(tokens), 'trailing target condition tokens')
    return result


def selected_graph(metadata, root, requested_features=None, target_cfg=None, rust_target=None):
    """Metadata must have been resolved with --filter-platform and recipe features."""
    require(metadata.get('version') == 1, 'unsupported cargo metadata schema')
    packages = indexed(metadata['packages'], 'id')
    nodes = indexed(metadata['resolve']['nodes'], 'id')
    require(root in packages and root in nodes, 'missing selected Cargo root')
    # Re-resolve features along runtime edges. Metadata includes weak optional
    # edges and feature unions from inactive/build/dev crates (notably SQLx).
    # Use Cargo's exact package IDs and matching declarations, evaluate retained
    # target conditions, and propagate only features of the runtime graph.
    features = {root: set(nodes[root]['features'] if requested_features is None else requested_features)}
    edges = set()
    changed = True
    while changed:
        changed = False
        for identity in list(features):
            package = packages[identity]
            enabled = features[identity]
            activated, requested = set(), {}
            pending = list(enabled)
            seen = set()
            while pending:
                feature = pending.pop()
                if feature in seen:
                    continue
                seen.add(feature)
                if feature.startswith('dep:'):
                    activated.add(feature[4:])
                elif '/' in feature:
                    name, child_feature = feature.split('/', 1)
                    weak = name.endswith('?')
                    name = name.rstrip('?')
                    requested.setdefault(name, set()).add(child_feature)
                    if not weak:
                        activated.add(name)
                else:
                    pending.extend(package.get('features', {}).get(feature, []))
            enabled.update(f for f in seen if not f.startswith('dep:') and '/' not in f)
            for dependency in nodes[identity]['deps']:
                target = dependency['pkg']
                require(target in packages and target in nodes, 'unknown Cargo dependency')
                active_kinds = [k for k in dependency['dep_kinds']
                                if k['kind'] is None and target_matches(k['target'], target_cfg, rust_target)]
                if not active_kinds:
                    continue
                kinds = {kind for t in packages[target]['targets'] for kind in t['kind']}
                if 'proc-macro' in kinds and not kinds & {'lib', 'rlib', 'dylib', 'cdylib', 'staticlib'}:
                    continue
                child_features = set()
                if 'dependencies' in package:
                    library_names = {t.get('name', packages[target]['name']).replace('-', '_')
                                     for t in packages[target]['targets']
                                     if set(t['kind']) & {'lib', 'rlib', 'dylib', 'cdylib', 'staticlib'}}
                    declarations = [d for d in package['dependencies']
                        if d['name'] == packages[target]['name']
                        and (d['rename'].replace('-', '_') == dependency['name'] if d.get('rename')
                             else dependency['name'] in library_names)
                        and any(k['kind'] is None and d['kind'] is None and k['target'] == d['target']
                                for k in active_kinds)]
                    require(declarations, 'resolved dependency has no declaration: ' + identity + ' -> ' + dependency['name'])
                    active = [d for d in declarations if not d['optional'] or (d.get('rename') or d['name']) in activated]
                    if not active:
                        continue
                    for declaration in active:
                        name = declaration.get('rename') or declaration['name']
                        child_features.update(declaration['features'])
                        child_features.update(requested.get(name, set()))
                        if declaration['uses_default_features']:
                            child_features.add('default')
                edges.add((identity, target))
                if target not in features or not child_features <= features[target]:
                    features.setdefault(target, set()).update(child_features)
                    changed = True
    return {key: packages[key] for key in sorted(features)}, sorted(edges)


def cargo_purl(package, revision):
    base = 'pkg:cargo/' + quote(package['name'], safe='') + '@' + quote(package['version'], safe='')
    source = package.get('source')
    if source in ('registry+https://github.com/rust-lang/crates.io-index', 'registry+https://index.crates.io/'):
        return base
    # Preserve registry/git/path identity, without exposing local build paths.
    if source is None:
        manifest = PurePosixPath(package['manifest_path'])
        try:
            relative = manifest.relative_to('/build')
        except ValueError as error:
            raise ValueError('workspace manifest is outside the source tree') from error
        require('..' not in relative.parts, 'unsafe workspace manifest path')
        source = 'workspace:' + revision + ':' + str(relative)
    require('@' not in source.split('://')[-1].split('/')[0], 'credentials in Cargo source')
    return base + '?repository_url=' + quote(source, safe='')


# Conservative SPDX expression parser. Unsupported conclusions stay NOASSERTION;
# full text remains in extracted licensing information, never guessed from names.
# SPDX 3.28.0 identifiers derived from cargo-about 0.9.2's locked spdx 0.13.4
# crate (SHA256 a8da593e30beb790fc9424502eb898320b44e5eb30367dbda1c1edde8e2f32d7).
# Refreshed with that reporting-tool parent; no runtime license database fetch.
LICENSE_IDS = set("""
0BSD 3D-Slicer-1.0 AAL ADSL AFL-1.1 AFL-1.2 AFL-2.0 AFL-2.1 AFL-3.0 AGPL-1.0 AGPL-1.0-only
AGPL-1.0-or-later AGPL-3.0 AGPL-3.0-only AGPL-3.0-or-later ALGLIB-Documentation AMD-newlib AMDPLPA
AML AML-glslang AMPAS ANTLR-PD ANTLR-PD-fallback APAFML APL-1.0 APSL-1.0 APSL-1.1 APSL-1.2 APSL-2.0
ASWF-Digital-Assets-1.0 ASWF-Digital-Assets-1.1 Abstyles AdaCore-doc Adobe-2006
Adobe-Display-PostScript Adobe-Glyph Adobe-Utopia Advanced-Cryptics-Dictionary Afmparse Aladdin
Apache-1.0 Apache-1.1 Apache-2.0 App-s2p Arphic-1999 Artistic-1.0 Artistic-1.0-Perl Artistic-1.0-cl8
Artistic-2.0 Artistic-dist Aspell-RU BOLA-1.1 BSD-1-Clause BSD-2-Clause BSD-2-Clause-Darwin
BSD-2-Clause-FreeBSD BSD-2-Clause-NetBSD BSD-2-Clause-Patent BSD-2-Clause-Views
BSD-2-Clause-first-lines BSD-2-Clause-pkgconf-disclaimer BSD-3-Clause BSD-3-Clause-Attribution
BSD-3-Clause-Clear BSD-3-Clause-HP BSD-3-Clause-LBNL BSD-3-Clause-Modification
BSD-3-Clause-No-Military-License BSD-3-Clause-No-Nuclear-License
BSD-3-Clause-No-Nuclear-License-2014 BSD-3-Clause-No-Nuclear-Warranty BSD-3-Clause-Open-MPI
BSD-3-Clause-Sun BSD-3-Clause-Tso BSD-3-Clause-acpica BSD-3-Clause-flex BSD-4-Clause
BSD-4-Clause-Shortened BSD-4-Clause-UC BSD-4.3RENO BSD-4.3TAHOE BSD-Advertising-Acknowledgement
BSD-Attribution-HPND-disclaimer BSD-Inferno-Nettverk BSD-Mark-Modifications BSD-Protection
BSD-Source-Code BSD-Source-beginning-file BSD-Systemics BSD-Systemics-W3Works BSL-1.0 BUSL-1.1
Baekmuk Bahyph Barr Beerware BitTorrent-1.0 BitTorrent-1.1 Bitstream-Charter Bitstream-Vera
BlueOak-1.0.0 Boehm-GC Boehm-GC-without-fee Borceux Brian-Gladman-2-Clause Brian-Gladman-3-Clause
Buddy C-UDA-1.0 CAL-1.0 CAL-1.0-Combined-Work-Exception CAPEC-tou CATOSL-1.1 CC-BY-1.0 CC-BY-2.0
CC-BY-2.5 CC-BY-2.5-AU CC-BY-3.0 CC-BY-3.0-AT CC-BY-3.0-AU CC-BY-3.0-DE CC-BY-3.0-IGO CC-BY-3.0-NL
CC-BY-3.0-US CC-BY-4.0 CC-BY-NC-1.0 CC-BY-NC-2.0 CC-BY-NC-2.5 CC-BY-NC-3.0 CC-BY-NC-3.0-DE
CC-BY-NC-4.0 CC-BY-NC-ND-1.0 CC-BY-NC-ND-2.0 CC-BY-NC-ND-2.5 CC-BY-NC-ND-3.0 CC-BY-NC-ND-3.0-DE
CC-BY-NC-ND-3.0-IGO CC-BY-NC-ND-4.0 CC-BY-NC-SA-1.0 CC-BY-NC-SA-2.0 CC-BY-NC-SA-2.0-DE
CC-BY-NC-SA-2.0-FR CC-BY-NC-SA-2.0-UK CC-BY-NC-SA-2.5 CC-BY-NC-SA-3.0 CC-BY-NC-SA-3.0-DE
CC-BY-NC-SA-3.0-IGO CC-BY-NC-SA-4.0 CC-BY-ND-1.0 CC-BY-ND-2.0 CC-BY-ND-2.5 CC-BY-ND-3.0
CC-BY-ND-3.0-DE CC-BY-ND-4.0 CC-BY-SA-1.0 CC-BY-SA-2.0 CC-BY-SA-2.0-UK CC-BY-SA-2.1-JP CC-BY-SA-2.5
CC-BY-SA-3.0 CC-BY-SA-3.0-AT CC-BY-SA-3.0-DE CC-BY-SA-3.0-IGO CC-BY-SA-4.0 CC-PDDC CC-PDM-1.0
CC-SA-1.0 CC0-1.0 CDDL-1.0 CDDL-1.1 CDL-1.0 CDLA-Permissive-1.0 CDLA-Permissive-2.0 CDLA-Sharing-1.0
CECILL-1.0 CECILL-1.1 CECILL-2.0 CECILL-2.1 CECILL-B CECILL-C CERN-OHL-1.1 CERN-OHL-1.2
CERN-OHL-P-2.0 CERN-OHL-S-2.0 CERN-OHL-W-2.0 CFITSIO CMU-Mach CMU-Mach-nodoc CNRI-Jython CNRI-Python
CNRI-Python-GPL-Compatible COIL-1.0 CPAL-1.0 CPL-1.0 CPOL-1.02 CUA-OPL-1.0 Caldera
Caldera-no-preamble Catharon ClArtistic Clips Community-Spec-1.0 Condor-1.1 Cornell-Lossless-JPEG
Cronyx Crossword CryptoSwift CrystalStacker Cube D-FSL-1.0 DEC-3-Clause DL-DE-BY-2.0 DL-DE-ZERO-2.0
DOC DRL-1.0 DRL-1.1 DSDP DocBook-DTD DocBook-Schema DocBook-Stylesheet DocBook-XML Dotseqn ECL-1.0
ECL-2.0 EFL-1.0 EFL-2.0 EPICS EPL-1.0 EPL-2.0 ESA-PL-permissive-2.4 ESA-PL-strong-copyleft-2.4
ESA-PL-weak-copyleft-2.4 EUDatagrid EUPL-1.0 EUPL-1.1 EUPL-1.2 Elastic-2.0 Entessa ErlPL-1.1 Eurosym
FBM FDK-AAC FSFAP FSFAP-no-warranty-disclaimer FSFUL FSFULLR FSFULLRSD FSFULLRWD FSL-1.1-ALv2
FSL-1.1-MIT FTL Fair Ferguson-Twofish Frameworx-1.0 FreeBSD-DOC FreeImage Furuseth GCR-docs GD
GFDL-1.1 GFDL-1.1-invariants GFDL-1.1-invariants-only GFDL-1.1-invariants-or-later
GFDL-1.1-no-invariants GFDL-1.1-no-invariants-only GFDL-1.1-no-invariants-or-later GFDL-1.1-only
GFDL-1.1-or-later GFDL-1.2 GFDL-1.2-invariants GFDL-1.2-invariants-only GFDL-1.2-invariants-or-later
GFDL-1.2-no-invariants GFDL-1.2-no-invariants-only GFDL-1.2-no-invariants-or-later GFDL-1.2-only
GFDL-1.2-or-later GFDL-1.3 GFDL-1.3-invariants GFDL-1.3-invariants-only GFDL-1.3-invariants-or-later
GFDL-1.3-no-invariants GFDL-1.3-no-invariants-only GFDL-1.3-no-invariants-or-later GFDL-1.3-only
GFDL-1.3-or-later GL2PS GLWTPL GPL-1.0 GPL-1.0+ GPL-1.0-only GPL-1.0-or-later GPL-2.0 GPL-2.0+
GPL-2.0-only GPL-2.0-or-later GPL-2.0-with-GCC-exception GPL-2.0-with-autoconf-exception
GPL-2.0-with-bison-exception GPL-2.0-with-classpath-exception GPL-2.0-with-font-exception GPL-3.0
GPL-3.0+ GPL-3.0-only GPL-3.0-or-later GPL-3.0-with-GCC-exception GPL-3.0-with-autoconf-exception
Game-Programming-Gems Giftware Glide Glulxe Graphics-Gems Gutmann HDF5 HIDAPI HP-1986 HP-1989 HPND
HPND-DEC HPND-Fenneberg-Livingston HPND-INRIA-IMAG HPND-Intel HPND-Kevlin-Henney HPND-MIT-disclaimer
HPND-Markus-Kuhn HPND-Netrek HPND-Pbmplus HPND-SMC HPND-UC HPND-UC-export-US HPND-doc HPND-doc-sell
HPND-export-US HPND-export-US-acknowledgement HPND-export-US-modify HPND-export2-US
HPND-merchantability-variant HPND-sell-MIT-disclaimer-xserver HPND-sell-regexpr HPND-sell-variant
HPND-sell-variant-MIT-disclaimer HPND-sell-variant-MIT-disclaimer-rev
HPND-sell-variant-critical-systems HTMLTIDY HaskellReport Hippocratic-2.1 IBM-pibs ICU
IEC-Code-Components-EULA IJG IJG-short IPA IPL-1.0 ISC ISC-Veillard ISO-permission ImageMagick
Imlib2 Info-ZIP Inner-Net-2.0 InnoSetup Intel Intel-ACPI Interbase-1.0 JPL-image JPNIC JSON Jam
JasPer-2.0 Kastrup Kazlib Knuth-CTAN LAL-1.2 LAL-1.3 LGPL-2.0 LGPL-2.0+ LGPL-2.0-only
LGPL-2.0-or-later LGPL-2.1 LGPL-2.1+ LGPL-2.1-only LGPL-2.1-or-later LGPL-3.0 LGPL-3.0+
LGPL-3.0-only LGPL-3.0-or-later LGPLLR LOOP LPD-document LPL-1.0 LPL-1.02 LPPL-1.0 LPPL-1.1 LPPL-1.2
LPPL-1.3a LPPL-1.3c LZMA-SDK-9.11-to-9.20 LZMA-SDK-9.22 Latex2e Latex2e-translated-notice Leptonica
LiLiQ-P-1.1 LiLiQ-R-1.1 LiLiQ-Rplus-1.1 Libpng Linux-OpenIB Linux-man-pages-1-para
Linux-man-pages-copyleft Linux-man-pages-copyleft-2-para Linux-man-pages-copyleft-var
Lucida-Bitmap-Fonts MIPS MIT MIT-0 MIT-CMU MIT-Click MIT-Festival MIT-Khronos-old MIT-Modern-Variant
MIT-STK MIT-Wu MIT-advertising MIT-enna MIT-feh MIT-open-group MIT-testregex MITNFA MMIXware
MMPL-1.0.1 MPEG-SSG MPL-1.0 MPL-1.1 MPL-2.0 MPL-2.0-no-copyleft-exception MS-LPL MS-PL MS-RL MTLL
Mackerras-3-Clause Mackerras-3-Clause-acknowledgment MakeIndex Martin-Birgmeier McPhee-slideshow
Minpack MirOS Motosoto MulanPSL-1.0 MulanPSL-2.0 Multics Mup NAIST-2003 NASA-1.3 NBPL-1.0 NCBI-PD
NCGL-UK-2.0 NCL NCSA NGPL NICTA-1.0 NIST-PD NIST-PD-TNT NIST-PD-fallback NIST-Software NLOD-1.0
NLOD-2.0 NLPL NOASSERTION NOSL NPL-1.0 NPL-1.1 NPOSL-3.0 NRL NTIA-PD NTP NTP-0 Naumen Net-SNMP
NetCDF Newsletr Nokia Noweb Nunit O-UDA-1.0 OAR OCCT-PL OCLC-2.0 ODC-By-1.0 ODbL-1.0 OFFIS OFL-1.0
OFL-1.0-RFN OFL-1.0-no-RFN OFL-1.1 OFL-1.1-RFN OFL-1.1-no-RFN OGC-1.0 OGDL-Taiwan-1.0 OGL-Canada-2.0
OGL-UK-1.0 OGL-UK-2.0 OGL-UK-3.0 OGTSL OLDAP-1.1 OLDAP-1.2 OLDAP-1.3 OLDAP-1.4 OLDAP-2.0 OLDAP-2.0.1
OLDAP-2.1 OLDAP-2.2 OLDAP-2.2.1 OLDAP-2.2.2 OLDAP-2.3 OLDAP-2.4 OLDAP-2.5 OLDAP-2.6 OLDAP-2.7
OLDAP-2.8 OLFL-1.3 OML OPL-1.0 OPL-UK-3.0 OPUBL-1.0 OSC-1.0 OSET-PL-2.1 OSL-1.0 OSL-1.1 OSL-2.0
OSL-2.1 OSL-3.0 OSSP OpenMDW-1.0 OpenPBS-2.3 OpenSSL OpenSSL-standalone OpenVision PADL PDDL-1.0
PHP-3.0 PHP-3.01 PPL PSF-2.0 ParaType-Free-Font-1.3 Parity-6.0.0 Parity-7.0.0 Pixar Plexus
PolyForm-Noncommercial-1.0.0 PolyForm-Small-Business-1.0.0 PostgreSQL Python-2.0 Python-2.0.1
QPL-1.0 QPL-1.0-INRIA-2004 Qhull RHeCos-1.1 RPL-1.1 RPL-1.5 RPSL-1.0 RSA-MD RSCPL Rdisc Ruby
Ruby-pty SAX-PD SAX-PD-2.0 SCEA SGI-B-1.0 SGI-B-1.1 SGI-B-2.0 SGI-OpenGL SGMLUG-PM SGP4 SHL-0.5
SHL-0.51 SISSL SISSL-1.2 SL SMAIL-GPL SMLNJ SMPPL SNIA SOFA SPL-1.0 SSH-OpenSSH SSH-short
SSLeay-standalone SSPL-1.0 SUL-1.0 SWL Saxpath SchemeReport Sendmail Sendmail-8.23
Sendmail-Open-Source-1.1 SimPL-2.0 Sleepycat Soundex Spencer-86 Spencer-94 Spencer-99 StandardML-NJ
SugarCRM-1.1.3 Sun-PPP Sun-PPP-2000 SunPro Symlinks TAPR-OHL-1.0 TCL TCP-wrappers TGPPL-1.0 TMate
TORQUE-1.1 TOSL TPDL TPL-1.0 TTWL TTYP0 TU-Berlin-1.0 TU-Berlin-2.0 TekHVC TermReadKey ThirdEye
TrustedQSL UCAR UCL-1.0 UMich-Merit UPL-1.0 URT-RLE Ubuntu-font-1.0 UnRAR Unicode-3.0
Unicode-DFS-2015 Unicode-DFS-2016 Unicode-TOU UnixCrypt Unlicense Unlicense-libtelnet
Unlicense-libwhirlpool VOSTROM VSL-1.0 Vim Vixie-Cron W3C W3C-19980720 W3C-20150513 WTFNMFPL WTFPL
Watcom-1.0 Widget-Workshop WordNet Wsuipa X11 X11-distribute-modifications-variant
X11-no-permit-persons X11-swapped XFree86-1.1 XSkat Xdebug-1.03 Xerox Xfig Xnet YPL-1.0 YPL-1.1
ZPL-1.1 ZPL-2.0 ZPL-2.1 Zed Zeeff Zend-2.0 Zimbra-1.3 Zimbra-1.4 Zlib any-OSI any-OSI-perl-modules
bcrypt-Solar-Designer blessing bzip2-1.0.5 bzip2-1.0.6 check-cvs checkmk copyleft-next-0.3.0
copyleft-next-0.3.1 curl cve-tou diffmark dtoa dvipdfm eCos-2.0 eGenix etalab-2.0 fwlw gSOAP-1.3b
generic-xts gnuplot gtkbook hdparm hyphen-bulgarian iMatix jove libpng-1.6.35 libpng-2.0
libselinux-1.0 libtiff libutil-David-Nugent lsof magaz mailprio man2html metamail mpi-permissive
mpich2 mplus ngrep pkgconf pnmstitch psfrag psutils python-ldap radvd snprintf softSurfer
ssh-keyscan swrule threeparttable ulem w3m wwl wxWindows xinetd xkeyboard-config-Zinoviev xlock xpp
xzoom zlib-acknowledgement
""".split())
EXCEPTION_IDS = set("""
389-exception Asterisk-exception Asterisk-linking-protocols-exception Autoconf-exception-2.0
Autoconf-exception-3.0 Autoconf-exception-generic Autoconf-exception-generic-3.0
Autoconf-exception-macro Bison-exception-1.24 Bison-exception-2.2 Bootloader-exception
CGAL-linking-exception CLISP-exception-2.0 Classpath-exception-2.0 Classpath-exception-2.0-short
DigiRule-FOSS-exception Digia-Qt-LGPL-exception-1.1 FLTK-exception Fawkes-Runtime-exception
Font-exception-2.0 GCC-exception-2.0 GCC-exception-2.0-note GCC-exception-3.1 GNAT-exception
GNOME-examples-exception GNU-compiler-exception GPL-3.0-389-ds-base-exception
GPL-3.0-interface-exception GPL-3.0-linking-exception GPL-3.0-linking-source-exception GPL-CC-1.0
GStreamer-exception-2005 GStreamer-exception-2008 Gmsh-exception Independent-modules-exception
KiCad-libraries-exception LGPL-3.0-linking-exception LLGPL LLVM-exception LZMA-exception
Libtool-exception Linux-syscall-note Nokia-Qt-exception-1.1 OCCT-exception-1.0
OCaml-LGPL-linking-exception OpenJDK-assembly-exception-1.0 PCRE2-exception
PS-or-PDF-font-exception-20170817 QPL-1.0-INRIA-2004-exception Qt-GPL-exception-1.0
Qt-LGPL-exception-1.1 Qwt-exception-1.0 RRDtool-FLOSS-exception-2.0 SANE-exception SHL-2.0 SHL-2.1
SWI-exception Simple-Library-Usage-exception Swift-exception Texinfo-exception UBDL-exception
Universal-FOSS-exception-1.0 WxWindows-exception-3.1 cryptsetup-OpenSSL-exception eCos-exception-2.0
erlang-otp-linking-exception fmt-exception freertos-exception-2.0 gnu-javamail-exception
harbour-exception i2p-gpl-java-exception kvirc-openssl-exception libpri-OpenH323-exception
mif-exception mxml-exception openvpn-openssl-exception polyparse-exception romic-exception
rsync-linking-exception sqlitestudio-OpenSSL-exception stunnel-exception u-boot-exception-2.0
vsftpd-openssl-exception x11vnc-openssl-exception
""".split())


def license_expression(value):
    if not isinstance(value, str) or not value:
        return 'NOASSERTION'
    tokens = re.findall(r'[A-Za-z0-9.+-]+|[()]', value)
    if ''.join(tokens) != re.sub(r'\s', '', value):
        return 'NOASSERTION'
    position = 0
    def term():
        nonlocal position
        if position >= len(tokens):
            return False
        token = tokens[position]; position += 1
        if token == '(':
            if not expression() or position >= len(tokens) or tokens[position] != ')':
                return False
            position += 1
            return True
        if token not in LICENSE_IDS:
            return False
        if position < len(tokens) and tokens[position] == 'WITH':
            position += 1
            if position >= len(tokens) or tokens[position] not in EXCEPTION_IDS:
                return False
            position += 1
        return True
    def expression():
        nonlocal position
        if not term():
            return False
        while position < len(tokens) and tokens[position] in ('AND', 'OR'):
            position += 1
            if not term():
                return False
        return True
    return value if expression() and position == len(tokens) else 'NOASSERTION'


def cargo_about_license_expressions(packages, report):
    """Return cargo-about's resolved SPDX expression keyed by full Cargo ID.

    cargo-about's JSON `crates` records carry the resolved expression, including
    clarifications. `licenses[].used_by` is only the selected notice text and
    cannot represent the full expression for alternatives such as `MIT OR
    Apache-2.0`.
    """
    crate_records = report.get('crates')
    require(isinstance(crate_records, list), 'malformed cargo-about crate list')
    resolved = {}
    for record in crate_records:
        require(isinstance(record, dict) and isinstance(record.get('package'), dict),
                'malformed cargo-about crate record')
        package = record['package']
        cargo_id = package.get('id')
        if cargo_id not in packages:
            continue
        require(cargo_id not in resolved, 'duplicate cargo-about Cargo identity: ' + str(cargo_id))
        component = packages[cargo_id]
        require(package.get('name') == component.get('name') and
                package.get('version') == component.get('version'),
                'cargo-about package identity mismatch: ' + cargo_id)
        expression = record.get('license')
        require(isinstance(expression, str) and expression not in ('', 'Unknown', 'Ignore', 'NOASSERTION'),
                'cargo-about did not resolve a crate license: ' + cargo_id)
        # SPDX deprecated the GNU version-only identifiers in favor of explicit
        # -only / -or-later forms. Keep the expression's operators and grouping.
        def canonical_identifier(match):
            token = match.group()
            if re.fullmatch(r'(?:A?GPL|LGPL|GFDL)-[0-9]+\.[0-9]+\+?', token):
                current = token.rstrip('+') + ('-or-later' if token.endswith('+') else '-only')
                if current in LICENSE_IDS:
                    return current
            return token
        expression = re.sub(r'[A-Za-z0-9.+-]+', canonical_identifier, expression)
        require(license_expression(expression) == expression,
                'cargo-about returned an unsupported SPDX expression for ' + cargo_id + ': ' + expression)
        resolved[cargo_id] = expression
    missing = set(packages) - set(resolved)
    require(not missing, 'selected Cargo graph lacks resolved cargo-about licenses: ' + ', '.join(sorted(missing)))
    return resolved


def validate_document(document):
    elements = [document, *document.get('packages', []), *document.get('files', [])]
    ids = indexed(elements, 'SPDXID')
    for relation in document.get('relationships', []):
        require(relation['spdxElementId'] in ids and relation['relatedSpdxElement'] in ids,
                'unresolved SPDX relationship')
    license_ids = indexed(document.get('hasExtractedLicensingInfos', []), 'licenseId')
    for element in elements:
        for key in ('licenseDeclared', 'licenseConcluded', 'licenseInfoFromFiles', 'licenseInfoInFiles'):
            values = element.get(key, [])
            if isinstance(values, str):
                values = [values]
            for value in values:
                for custom in re.findall(r'LicenseRef-[A-Za-z0-9.-]+', value):
                    require(custom in license_ids, 'unresolved custom license reference')
        for checksum in element.get('checksums', []):
            if checksum['algorithm'] == 'SHA256':
                require(re.fullmatch('[a-fA-F0-9]{64}', checksum['checksumValue']), 'invalid SPDX checksum')


def scan_cargo_lock(lock_path):
    """Use the generator's Syft binary, scoped to one verified lockfile.

    Image catalogers omit Cargo.lock; scanning the whole builder would include
    reporting tools and registry fixtures. A file source preserves Cargo.lock's
    basename while making those unrelated lockfiles inaccessible to this scan.
    """
    completed = subprocess.run([
        'syft', 'file:' + str(lock_path), '--quiet',
        '--override-default-catalogers', 'rust-cargo-lock-cataloger',
        '--output', 'syft-json',
    ], check=True, capture_output=True)
    report = parse_json(completed.stdout)
    descriptor = report['descriptor']
    require(descriptor['name'] == 'syft' and descriptor.get('version'), 'missing Syft identity')
    packages = {}
    for artifact in report['artifacts']:
        require(artifact.get('type') == 'rust-crate'
                and artifact.get('foundBy') == 'rust-cargo-lock-cataloger',
                'unexpected Syft Cargo cataloger output')
        metadata = artifact['metadata']
        require(all(artifact[field] == metadata[field] for field in ('name', 'version')),
                'Syft Cargo metadata identity mismatch')
        key = (artifact['name'], artifact['version'], metadata.get('source') or '')
        require(key not in packages, 'duplicate Syft Cargo identity')
        packages[key] = artifact
    require(packages, 'empty Syft Cargo inventory')
    evidence = {'version': descriptor['version'], 'cataloger': 'rust-cargo-lock-cataloger',
                'sha256': sha256(completed.stdout), 'package_count': len(packages)}
    return packages, evidence


def augment_spdx(document, context):
    require(context.api_version == 1, 'unsupported hook API')
    evidence = Path(context.builder_path) / 'build/pgrx-sbom'
    manifest = parse_json(safe_file(context.builder_path, 'build/pgrx-sbom/manifest.json').read_bytes())
    require(manifest.get('schema_version') == 2, 'unsupported evidence schema')
    identity, target, build = manifest['identity'], manifest['target'], manifest['build']
    for key in ('extension', 'sql_name', 'source_version', 'sql_version', 'repository', 'revision', 'archive_sha256'):
        require(isinstance(identity.get(key), str) and identity[key], f'missing identity: {key}')
    require(re.fullmatch('[a-f0-9]{40}', identity['revision']), 'invalid source revision')
    require(re.fullmatch('[a-f0-9]{64}', identity['archive_sha256']), 'invalid source archive hash')
    require(context.extension_name in ('extension', identity['extension']), 'extension identity mismatch')
    require(target['platform'] == context.platform and target['platform'] in TARGETS, 'platform mismatch')
    triple, machine = TARGETS[target['platform']]
    require(target['rust_target'] == triple, 'Rust target mismatch')
    require(str(target['pg_major']).isdigit() and target['distro'] in ('bookworm', 'trixie'), 'invalid target')
    require(isinstance(build['default_features'], bool) and isinstance(build['features'], list), 'invalid feature policy')
    require(build['profile'] == 'release', 'unsupported build profile')
    checked_bytes(context.builder_path, 'build/Cargo.lock', manifest['inputs']['lock_sha256'])
    reports = {}
    for name in ('cargo-metadata', 'cargo-about'):
        entry = manifest['reports'][name]
        reports[name] = parse_json(checked_bytes(evidence, entry['path'], entry['sha256']))
    require(isinstance(reports['cargo-about'].get('licenses'), list), 'malformed cargo-about report')
    cfg = build['target_cfg']
    require(isinstance(cfg, list) and all(isinstance(fact, str) for fact in cfg), 'invalid target configuration')
    expected_arch = 'x86_64' if target['platform'] == 'linux/amd64' else 'aarch64'
    for key, value in [('target_arch', expected_arch), ('target_os', 'linux'), ('target_env', 'gnu'), ('target_pointer_width', '64')]:
        require([fact for fact in cfg if fact.startswith(key + '=')] == [key + '=' + json.dumps(value)], 'target configuration mismatch: ' + key)
    packages, edges = selected_graph(reports['cargo-metadata'], build['root_id'],
                                    build['features'] + (['default'] if build['default_features'] else []), cfg, triple)
    about_licenses = cargo_about_license_expressions(packages, reports['cargo-about'])
    root_component = packages[build['root_id']]
    syft_packages, syft_evidence = scan_cargo_lock(safe_file(context.builder_path, 'build/Cargo.lock'))
    selected_syft = {}
    for key, package in packages.items():
        locked_identity = (package['name'], package['version'], package.get('source') or '')
        require(locked_identity in syft_packages, 'selected Cargo identity missing from Syft: ' + key)
        selected_syft[key] = syft_packages[locked_identity]
    require(root_component['name'] == identity['sql_name'] and root_component['version'] == identity['sql_version'], 'Cargo root identity mismatch')
    nodes = indexed(reports['cargo-metadata']['resolve']['nodes'], 'id')
    features = nodes[build['root_id']]['features']
    require('pg'+str(target['pg_major']) in features, 'selected PG feature missing')
    require(set(build['features']) <= set(features), 'selected feature missing')
    require(('default' in features) == build['default_features'], 'default feature policy mismatch')
    result = deepcopy(document)
    files = indexed(result['files'], 'fileName')
    mapped, has_library = set(), False
    for payload in manifest['payload']:
        name = payload['final']
        require(name not in mapped, 'duplicate payload mapping'); mapped.add(name)
        builder_bytes = checked_bytes(context.builder_path, payload['builder'], payload['sha256'])
        final_bytes = checked_bytes(context.final_path, name, payload['sha256'])
        require(builder_bytes == final_bytes, 'payload binding mismatch')
        file = files.get(name) or files.get('./'+name)
        require(file is not None, 'payload missing from generator inventory')
        require(any(c['algorithm'] == 'SHA256' and c['checksumValue'].lower() == payload['sha256'] for c in file['checksums']), 'generator checksum mismatch')
        if payload['kind'] == 'library':
            has_library = True
            require(len(final_bytes) >= 20 and final_bytes[:6] == b'\x7fELF\x02\x01' and int.from_bytes(final_bytes[18:20], 'little') == machine, 'ELF architecture mismatch')
    require(has_library, 'missing compiled library binding')
    ids = {}
    for key, component in packages.items():
        purl = cargo_purl(component, identity['revision'])
        package = {'SPDXID': 'SPDXRef-Cargo-'+sha256(purl.encode())[:32], 'filesAnalyzed': False,
                   'downloadLocation': 'NOASSERTION', 'copyrightText': 'NOASSERTION',
                   'licenseConcluded': 'NOASSERTION'}
        result['packages'].append(package)
        package['name'] = selected_syft[key]['name']; package['versionInfo'] = selected_syft[key]['version']
        # cargo-about resolves package-specific declarations and configured
        # clarifications. This preserves full AND/OR expressions while filling
        # missing or inaccurate Cargo metadata uniformly for every crate.
        package['licenseDeclared'] = about_licenses[key]
        ref = {'referenceCategory': 'PACKAGE-MANAGER', 'referenceType': 'purl', 'referenceLocator': purl}
        if ref not in package.setdefault('externalRefs', []):
            package['externalRefs'].append(ref)
        ids[key] = package['SPDXID']
    relationships = result.setdefault('relationships', [])
    # The root crate represents the shipped extension. Individual file records
    # retain their own checksums and Syft metadata without synthetic ownership.
    root_id = ids[build['root_id']]
    describes_root = {'spdxElementId': result['SPDXID'], 'relationshipType': 'DESCRIBES',
                      'relatedSpdxElement': root_id}
    if describes_root not in relationships:
        relationships.append(describes_root)
    for source, dest in edges:
        relationships.append({'spdxElementId': ids[source], 'relationshipType': 'DEPENDS_ON', 'relatedSpdxElement': ids[dest]})
    # License associations are keyed by full Cargo ID, never ambiguous name/version.
    licensed = set()
    for evidence_license in manifest['licenses']:
        key = evidence_license['cargo_id']
        require(key in packages, 'license belongs to unselected dependency')
        text = checked_bytes(context.final_path, evidence_license['final'], evidence_license['sha256']).decode('utf-8')
        require(any(record.get('id') == evidence_license['name'] and record.get('text') == text and any(use.get('crate', {}).get('id') == key for use in record.get('used_by', [])) for record in reports['cargo-about']['licenses']), 'license association does not match cargo-about evidence')
        licensed.add(key)
        license_id = 'LicenseRef-Cargo-'+sha256(text.encode())[:32]
        extracted = {'licenseId': license_id, 'extractedText': text, 'name': evidence_license['name']}
        infos = result.setdefault('hasExtractedLicensingInfos', [])
        if not any(info['licenseId'] == license_id for info in infos):
            infos.append(extracted)
        package = next(p for p in result['packages'] if p['SPDXID'] == ids[key])
        package.setdefault('attributionTexts', []).append('Cargo license text: '+license_id)
    require(licensed == set(packages), 'selected dependencies missing shipped license evidence')
    annotation = {'namespace': NAMESPACE, 'schema_version': 1, 'identity': identity, 'target': target,
                  'build': {k: v for k, v in build.items() if k != 'root_id'},
                  'root_purl': cargo_purl(root_component, identity['revision']), 'syft_cargo_lock': syft_evidence,
                  'reports': {k: v['sha256'] for k, v in manifest['reports'].items()},
                  'payload': manifest['payload'], 'lock_sha256': manifest['inputs']['lock_sha256']}
    result.setdefault('annotations', []).append({'annotationType': 'OTHER', 'annotator': 'Tool: cnpg-pgrx-hook-v1',
        'annotationDate': result['creationInfo']['created'], 'comment': json.dumps(annotation, sort_keys=True, separators=(',', ':'))})
    result['relationships'] = sorted({json.dumps(r, sort_keys=True): r for r in relationships}.values(), key=lambda r: (r['spdxElementId'], r['relationshipType'], r['relatedSpdxElement']))
    result['packages'].sort(key=lambda p: p['SPDXID'])
    return result
