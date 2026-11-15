#!/usr/bin/env bash
set -euo pipefail

# Reviewed for the source revisions guarded by evidence.py. These are explicit
# notice locations and ranges, not dependency discovery or a comment parser.
duckdb=/build/third_party/duckdb
mkdir -p /licenses/{pg_duckdb,duckdb,brotli,lz4,mbedtls,snappy,yyjson,zstd,xxhash}

# pg_duckdb
{
    printf '\nFiles: %s\n\n' LICENSE
    cat "/build/LICENSE"
    printf '\nFiles: %s\n\n' NOTICE
    cat "/build/NOTICE"
    printf '\nFiles: %s\n\n' PostgreSQL/copyright
    cat "/usr/share/doc/postgresql-server-dev-${PG_MAJOR}/copyright"
    cat /usr/share/common-licenses/GPL-1 /usr/share/common-licenses/Artistic
    printf '\nFiles: %s\n\n' src/vendor/pg_explain.cpp
    sed -n 1,10p "/build/src/vendor/pg_explain.cpp"
    printf '\nFiles: %s\n\n' src/vendor/pg_ruleutils_14.c
    sed -n 1,11p "/build/src/vendor/pg_ruleutils_14.c"
    printf '\nFiles: %s\n\n' src/vendor/pg_ruleutils_15.c
    sed -n 1,11p "/build/src/vendor/pg_ruleutils_15.c"
    printf '\nFiles: %s\n\n' src/vendor/pg_ruleutils_16.c
    sed -n 1,11p "/build/src/vendor/pg_ruleutils_16.c"
    printf '\nFiles: %s\n\n' src/vendor/pg_ruleutils_17.c
    sed -n 1,11p "/build/src/vendor/pg_ruleutils_17.c"
    printf '\nFiles: %s\n\n' src/vendor/pg_ruleutils_18.c
    sed -n 1,11p "/build/src/vendor/pg_ruleutils_18.c"
    printf '\nFiles: %s\n\n' src/vendor/pg_ruleutils_19.c
    sed -n 1,11p "/build/src/vendor/pg_ruleutils_19.c"
} > /licenses/pg_duckdb/copyright

# duckdb
{
    # Debian source-package copyright baseline, including common-license texts.
    curl -fsSL https://deb.debian.org/debian/pool/main/d/duckdb/duckdb_2.0.0+dfsg2-1.debian.tar.xz \
        | tar -xJO debian/copyright
    cat /usr/share/common-licenses/Apache-2.0 /usr/share/common-licenses/GPL-2
    printf '\nFiles: %s\n\n' LICENSE
    cat "$duckdb/LICENSE"
    printf '\nFiles: %s\n\n' 'Unicode Character Database/LICENSE'
    printf 'Notice-Source: %s\n\n' https://www.unicode.org/license.txt
    curl -fsSL https://www.unicode.org/license.txt
    printf '\nFiles: %s\n\n' adbc/LICENSE.txt
    printf 'Notice-Source: %s\n\n' https://raw.githubusercontent.com/apache/arrow-adbc/89fe37cf2050202685398cb50502e31a4d293306/LICENSE.txt
    curl -fsSL https://raw.githubusercontent.com/apache/arrow-adbc/89fe37cf2050202685398cb50502e31a4d293306/LICENSE.txt
    printf '\nFiles: %s\n\n' adbc/NOTICE.txt
    printf 'Notice-Source: %s\n\n' https://raw.githubusercontent.com/apache/arrow-adbc/89fe37cf2050202685398cb50502e31a4d293306/NOTICE.txt
    curl -fsSL https://raw.githubusercontent.com/apache/arrow-adbc/89fe37cf2050202685398cb50502e31a4d293306/NOTICE.txt
    printf '\nFiles: %s\n\n' cldr/LICENSE
    printf 'Notice-Source: %s\n\n' https://raw.githubusercontent.com/unicode-org/cldr/release-48/LICENSE
    curl -fsSL https://raw.githubusercontent.com/unicode-org/cldr/release-48/LICENSE
    printf '\nFiles: %s\n\n' nanoarrow/NOTICE.txt
    printf 'Notice-Source: %s\n\n' https://raw.githubusercontent.com/apache/arrow-nanoarrow/ee22361fa22581e9b8e26cc0c0a37134ffdcfba2/NOTICE.txt
    curl -fsSL https://raw.githubusercontent.com/apache/arrow-nanoarrow/ee22361fa22581e9b8e26cc0c0a37134ffdcfba2/NOTICE.txt
    printf '\nFiles: %s\n\n' robin-hood-hashing/LICENSE
    printf 'Notice-Source: %s\n\n' https://raw.githubusercontent.com/martinus/robin-hood-hashing/3.11.5/LICENSE
    curl -fsSL https://raw.githubusercontent.com/martinus/robin-hood-hashing/3.11.5/LICENSE
    printf '\nFiles: %s\n\n' src/common/adbc/nanoarrow/allocator.cpp
    sed -n 1,16p "$duckdb/src/common/adbc/nanoarrow/allocator.cpp"
    printf '\nFiles: %s\n\n' src/common/checksum.cpp
    sed -n 11,13p "$duckdb/src/common/checksum.cpp"
    printf '\nFiles: %s\n\n' src/common/crypto/md5.cpp
    sed -n 6,21p "$duckdb/src/common/crypto/md5.cpp"
    printf '\nFiles: %s\n\n' src/common/types/hash.cpp
    sed -n '79,81p;119,121p' "$duckdb/src/common/types/hash.cpp"
    printf '\nFiles: %s\n\n' src/include/duckdb/execution/merge_sort_tree.hpp
    sed -n '/^\/\/ MIT License Text:$/,/^\/\/ SOFTWARE\.$/p' "$duckdb/src/include/duckdb/execution/merge_sort_tree.hpp"
    printf '\nFiles: %s\n\n' src/include/duckdb/storage/compression/alp/algorithm/LICENSE
    cat "$duckdb/src/include/duckdb/storage/compression/alp/algorithm/LICENSE"
    printf '\nFiles: %s\n\n' src/storage/compression/bitpacking.cpp
    sed -n 651,651p "$duckdb/src/storage/compression/bitpacking.cpp"
    printf '\nFiles: %s\n\n' third_party/concurrentqueue/LICENSE
    cat "$duckdb/third_party/concurrentqueue/LICENSE"
    printf '\nFiles: %s\n\n' third_party/concurrentqueue/blockingconcurrentqueue.h
    sed -n 1,5p "$duckdb/third_party/concurrentqueue/blockingconcurrentqueue.h"
    printf '\nFiles: %s\n\n' third_party/concurrentqueue/concurrentqueue.h
    sed -n 7,28p "$duckdb/third_party/concurrentqueue/concurrentqueue.h"
    printf '\nFiles: %s\n\n' third_party/concurrentqueue/lightweightsemaphore.h
    sed -n '1,4p;/^\/\/ Code in the mpmc_sema namespace/,/^\/\/ 3\. This notice may not be removed/p' "$duckdb/third_party/concurrentqueue/lightweightsemaphore.h"
    printf '\nFiles: %s\n\n' third_party/fast_float/LICENSE
    cat "$duckdb/third_party/fast_float/LICENSE"
    printf '\nFiles: %s\n\n' third_party/fast_float/fast_float/fast_float.h
    sed -n 13,35p "$duckdb/third_party/fast_float/fast_float/fast_float.h"
    printf '\nFiles: %s\n\n' third_party/fastpforlib/LICENSE
    cat "$duckdb/third_party/fastpforlib/LICENSE"
    printf '\nFiles: %s\n\n' third_party/fastpforlib/bitpacking.h
    sed -n 1,6p "$duckdb/third_party/fastpforlib/bitpacking.h"
    printf '\nFiles: %s\n\n' third_party/fastpforlib/bitpackinghelpers.h
    sed -n 1,6p "$duckdb/third_party/fastpforlib/bitpackinghelpers.h"
    printf '\nFiles: %s\n\n' third_party/fmt/LICENSE
    cat "$duckdb/third_party/fmt/LICENSE"
    printf '\nFiles: %s\n\n' third_party/fmt/format.cc
    sed -n 1,6p "$duckdb/third_party/fmt/format.cc"
    printf '\nFiles: %s\n\n' third_party/fmt/include/fmt/core.h
    sed -n 1,6p "$duckdb/third_party/fmt/include/fmt/core.h"
    printf '\nFiles: %s\n\n' third_party/fmt/include/fmt/format-inl.h
    sed -n 1,6p "$duckdb/third_party/fmt/include/fmt/format-inl.h"
    printf '\nFiles: %s\n\n' third_party/fmt/include/fmt/format.h
    sed -n 1,31p "$duckdb/third_party/fmt/include/fmt/format.h"
    printf '\nFiles: %s\n\n' third_party/fmt/include/fmt/ostream.h
    sed -n 1,6p "$duckdb/third_party/fmt/include/fmt/ostream.h"
    printf '\nFiles: %s\n\n' third_party/fmt/include/fmt/printf.h
    sed -n 1,6p "$duckdb/third_party/fmt/include/fmt/printf.h"
    printf '\nFiles: %s\n\n' third_party/fsst/LICENSE
    cat "$duckdb/third_party/fsst/LICENSE"
    printf '\nFiles: %s\n\n' third_party/fsst/fsst.h
    sed -n 1,47p "$duckdb/third_party/fsst/fsst.h"
    printf '\nFiles: %s\n\n' third_party/fsst/libfsst.cpp
    sed -n 1,17p "$duckdb/third_party/fsst/libfsst.cpp"
    printf '\nFiles: %s\n\n' third_party/fsst/libfsst.hpp
    sed -n 1,17p "$duckdb/third_party/fsst/libfsst.hpp"
    printf '\nFiles: %s\n\n' third_party/httplib/LICENSE
    cat "$duckdb/third_party/httplib/LICENSE"
    printf '\nFiles: %s\n\n' third_party/httplib/httplib.hpp
    sed -n 1,6p "$duckdb/third_party/httplib/httplib.hpp"
    printf '\nFiles: %s\n\n' third_party/hyperloglog/LICENSE
    cat "$duckdb/third_party/hyperloglog/LICENSE"
    printf '\nFiles: %s\n\n' third_party/hyperloglog/hyperloglog.cpp
    sed -n 1,30p "$duckdb/third_party/hyperloglog/hyperloglog.cpp"
    printf '\nFiles: %s\n\n' third_party/hyperloglog/sds.cpp
    sed -n 1,31p "$duckdb/third_party/hyperloglog/sds.cpp"
    printf '\nFiles: %s\n\n' third_party/jaro_winkler/LICENSE
    cat "$duckdb/third_party/jaro_winkler/LICENSE"
    printf '\nFiles: %s\n\n' third_party/jaro_winkler/details/common.hpp
    sed -n '1,1p;2,2p' "$duckdb/third_party/jaro_winkler/details/common.hpp"
    printf '\nFiles: %s\n\n' third_party/jemalloc/LICENSE
    cat "$duckdb/third_party/jemalloc/LICENSE"
    printf '\nFiles: %s\n\n' third_party/jemalloc/include/jemalloc/internal/hash.h
    sed -n 7,11p "$duckdb/third_party/jemalloc/include/jemalloc/internal/hash.h"
    printf '\nFiles: %s\n\n' third_party/jemalloc/include/msvc_compat/C99/stdint.h
    sed -n 1,30p "$duckdb/third_party/jemalloc/include/msvc_compat/C99/stdint.h"
    printf '\nFiles: %s\n\n' third_party/miniz/LICENSE
    cat "$duckdb/third_party/miniz/LICENSE"
    printf '\nFiles: %s\n\n' third_party/miniz/miniz.cpp
    sed -n '1,25p;574,599p;600,624p;2049,2051p;2883,2908p' "$duckdb/third_party/miniz/miniz.cpp"
    printf '\nFiles: %s\n\n' third_party/miniz/miniz.hpp
    sed -n 1,112p "$duckdb/third_party/miniz/miniz.hpp"
    printf '\nFiles: %s\n\n' third_party/parquet/LICENSE
    cat "$duckdb/third_party/parquet/LICENSE"
    printf '\nFiles: %s\n\n' third_party/pcg/LICENSE
    cat "$duckdb/third_party/pcg/LICENSE"
    printf '\nFiles: %s\n\n' third_party/pcg/pcg_extras.hpp
    sed -n 1,20p "$duckdb/third_party/pcg/pcg_extras.hpp"
    printf '\nFiles: %s\n\n' third_party/pcg/pcg_random.hpp
    sed -n 1,20p "$duckdb/third_party/pcg/pcg_random.hpp"
    printf '\nFiles: %s\n\n' third_party/pdqsort/LICENSE
    cat "$duckdb/third_party/pdqsort/LICENSE"
    printf '\nFiles: %s\n\n' third_party/pdqsort/pdqsort.h
    sed -n 1,20p "$duckdb/third_party/pdqsort/pdqsort.h"
    printf '\nFiles: %s\n\n' third_party/re2/LICENSE
    cat "$duckdb/third_party/re2/LICENSE"
    printf '\nFiles: %s\n\n' third_party/re2/re2/bitmap256.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/bitmap256.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/bitmap256.h
    sed -n 1,3p "$duckdb/third_party/re2/re2/bitmap256.h"
    printf '\nFiles: %s\n\n' third_party/re2/re2/bitstate.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/bitstate.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/compile.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/compile.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/filtered_re2.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/filtered_re2.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/nfa.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/nfa.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/parse.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/parse.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/pod_array.h
    sed -n 1,3p "$duckdb/third_party/re2/re2/pod_array.h"
    printf '\nFiles: %s\n\n' third_party/re2/re2/re2.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/re2.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/set.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/set.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/stringpiece.cc
    sed -n 1,3p "$duckdb/third_party/re2/re2/stringpiece.cc"
    printf '\nFiles: %s\n\n' third_party/re2/re2/stringpiece.h
    sed -n 1,3p "$duckdb/third_party/re2/re2/stringpiece.h"
    printf '\nFiles: %s\n\n' third_party/re2/util/rune.cc
    sed -n 1,13p "$duckdb/third_party/re2/util/rune.cc"
    printf '\nFiles: %s\n\n' third_party/re2/util/strutil.cc
    sed -n 1,3p "$duckdb/third_party/re2/util/strutil.cc"
    printf '\nFiles: %s\n\n' third_party/re2/util/utf.h
    sed -n 1,16p "$duckdb/third_party/re2/util/utf.h"
    printf '\nFiles: %s\n\n' third_party/ska_sort/LICENSE
    cat "$duckdb/third_party/ska_sort/LICENSE"
    printf '\nFiles: %s\n\n' third_party/ska_sort/ska_sort.hpp
    sed -n 1,3p "$duckdb/third_party/ska_sort/ska_sort.hpp"
    printf '\nFiles: %s\n\n' third_party/skiplist/HeadNode.h
    sed -n '1,33p;50,72p' "$duckdb/third_party/skiplist/HeadNode.h"
    printf '\nFiles: %s\n\n' third_party/skiplist/IntegrityEnums.h
    sed -n 4,38p "$duckdb/third_party/skiplist/IntegrityEnums.h"
    printf '\nFiles: %s\n\n' third_party/skiplist/LICENSE
    cat "$duckdb/third_party/skiplist/LICENSE"
    printf '\nFiles: %s\n\n' third_party/skiplist/Node.h
    sed -n 1,35p "$duckdb/third_party/skiplist/Node.h"
    printf '\nFiles: %s\n\n' third_party/skiplist/NodeRefs.h
    sed -n 1,7p "$duckdb/third_party/skiplist/NodeRefs.h"
    printf '\nFiles: %s\n\n' third_party/skiplist/RollingMedian.h
    sed -n 4,38p "$duckdb/third_party/skiplist/RollingMedian.h"
    printf '\nFiles: %s\n\n' third_party/skiplist/SkipList.cpp
    sed -n 1,7p "$duckdb/third_party/skiplist/SkipList.cpp"
    printf '\nFiles: %s\n\n' third_party/skiplist/SkipList.h
    sed -n 4,36p "$duckdb/third_party/skiplist/SkipList.h"
    printf '\nFiles: %s\n\n' third_party/tdigest/LICENSE
    cat "$duckdb/third_party/tdigest/LICENSE"
    printf '\nFiles: %s\n\n' third_party/tdigest/NOTICES
    cat "$duckdb/third_party/tdigest/NOTICES"
    printf '\nFiles: %s\n\n' third_party/tdigest/t_digest.hpp
    sed -n 1,16p "$duckdb/third_party/tdigest/t_digest.hpp"
    printf '\nFiles: %s\n\n' third_party/thrift/thrift/LICENSE
    cat "$duckdb/third_party/thrift/thrift/LICENSE"
    printf '\nFiles: %s\n\n' third_party/thrift/thrift/TApplicationException.h
    sed -n 1,18p "$duckdb/third_party/thrift/thrift/TApplicationException.h"
    printf '\nFiles: %s\n\n' third_party/utf8proc/LICENSE
    cat "$duckdb/third_party/utf8proc/LICENSE"
    printf '\nFiles: %s\n\n' third_party/utf8proc/include/utf8proc.hpp
    sed -n '1,22p;25,49p' "$duckdb/third_party/utf8proc/include/utf8proc.hpp"
    printf '\nFiles: %s\n\n' third_party/utf8proc/utf8proc.cpp
    sed -n '2,23p;25,33p' "$duckdb/third_party/utf8proc/utf8proc.cpp"
    printf '\nFiles: %s\n\n' third_party/vergesort/LICENSE
    cat "$duckdb/third_party/vergesort/LICENSE"
    printf '\nFiles: %s\n\n' third_party/vergesort/detail/insertion_sort.h
    sed -n 1,21p "$duckdb/third_party/vergesort/detail/insertion_sort.h"
    printf '\nFiles: %s\n\n' third_party/vergesort/detail/is_sorted_until.h
    sed -n 1,25p "$duckdb/third_party/vergesort/detail/is_sorted_until.h"
    printf '\nFiles: %s\n\n' third_party/vergesort/vergesort.h
    sed -n 1,25p "$duckdb/third_party/vergesort/vergesort.h"
    printf '\nFiles: %s\n\n' tzdata/LICENSE
    printf 'Notice-Source: %s\n\n' https://raw.githubusercontent.com/unicode-org/icu-data/6eac2f4d349d9f4a0825103bb41845d8e5ab7add/LICENSE
    curl -fsSL https://raw.githubusercontent.com/unicode-org/icu-data/6eac2f4d349d9f4a0825103bb41845d8e5ab7add/LICENSE
} > /licenses/duckdb/copyright

# brotli
{
    printf '\nFiles: %s\n\n' third_party/brotli/LICENSE
    cat "$duckdb/third_party/brotli/LICENSE"
    printf '\nFiles: %s\n\n' third_party/brotli/common/brotli_constants.h
    sed -n 1,5p "$duckdb/third_party/brotli/common/brotli_constants.h"
    printf '\nFiles: %s\n\n' third_party/brotli/common/brotli_platform.h
    sed -n 1,5p "$duckdb/third_party/brotli/common/brotli_platform.h"
    printf '\nFiles: %s\n\n' third_party/brotli/common/constants.cpp
    sed -n 1,5p "$duckdb/third_party/brotli/common/constants.cpp"
    printf '\nFiles: %s\n\n' third_party/brotli/common/shared_dictionary.cpp
    sed -n 1,5p "$duckdb/third_party/brotli/common/shared_dictionary.cpp"
    printf '\nFiles: %s\n\n' third_party/brotli/dec/state.cpp
    sed -n 1,5p "$duckdb/third_party/brotli/dec/state.cpp"
    printf '\nFiles: %s\n\n' third_party/brotli/enc/brotli_bit_stream.cpp
    sed -n 1,5p "$duckdb/third_party/brotli/enc/brotli_bit_stream.cpp"
    printf '\nFiles: %s\n\n' third_party/brotli/enc/brotli_hash.h
    sed -n '1,5p;249,253p;3137,3141p' "$duckdb/third_party/brotli/enc/brotli_hash.h"
    printf '\nFiles: %s\n\n' third_party/brotli/enc/entropy_encode.cpp
    sed -n 1,5p "$duckdb/third_party/brotli/enc/entropy_encode.cpp"
    printf '\nFiles: %s\n\n' third_party/brotli/enc/state.h
    sed -n 1,5p "$duckdb/third_party/brotli/enc/state.h"
} > /licenses/brotli/copyright

# lz4
{
    printf '\nFiles: %s\n\n' third_party/lz4/LICENSE
    cat "$duckdb/third_party/lz4/LICENSE"
    printf '\nFiles: %s\n\n' third_party/lz4/lz4.cpp
    sed -n 1,33p "$duckdb/third_party/lz4/lz4.cpp"
    printf '\nFiles: %s\n\n' third_party/lz4/lz4.hpp
    sed -n 1,34p "$duckdb/third_party/lz4/lz4.hpp"
} > /licenses/lz4/copyright

# mbedtls
{
    printf '\nFiles: %s\n\n' third_party/mbedtls/LICENSE
    cat "$duckdb/third_party/mbedtls/LICENSE"
    printf '\nFiles: %s\n\n' third_party/mbedtls/include/mbedtls/aes.h
    sed -n 23,26p "$duckdb/third_party/mbedtls/include/mbedtls/aes.h"
    printf '\nFiles: %s\n\n' third_party/mbedtls/include/mbedtls/des.h
    sed -n 10,14p "$duckdb/third_party/mbedtls/include/mbedtls/des.h"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/aes.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/aes.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/asn1parse.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/asn1parse.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/asn1write.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/asn1write.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/base64.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/base64.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/bignum.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/bignum.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/bignum_core.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/bignum_core.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/cipher.cpp
    sed -n 1,10p "$duckdb/third_party/mbedtls/library/cipher.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/cipher_wrap.cpp
    sed -n 1,10p "$duckdb/third_party/mbedtls/library/cipher_wrap.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/constant_time.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/constant_time.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/ctr.h
    sed -n 1,8p "$duckdb/third_party/mbedtls/library/ctr.h"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/gcm.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/gcm.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/md.cpp
    sed -n 1,10p "$duckdb/third_party/mbedtls/library/md.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/oid.cpp
    sed -n 1,8p "$duckdb/third_party/mbedtls/library/oid.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/pem.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/pem.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/pk.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/pk.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/pk_wrap.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/pk_wrap.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/pkparse.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/pkparse.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/platform.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/platform.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/platform_util.cpp
    sed -n 1,7p "$duckdb/third_party/mbedtls/library/platform_util.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/rsa.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/rsa.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/rsa_alt_helpers.cpp
    sed -n 1,7p "$duckdb/third_party/mbedtls/library/rsa_alt_helpers.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/sha1.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/sha1.cpp"
    printf '\nFiles: %s\n\n' third_party/mbedtls/library/sha256.cpp
    sed -n 1,6p "$duckdb/third_party/mbedtls/library/sha256.cpp"
} > /licenses/mbedtls/copyright

# snappy
{
    printf '\nFiles: %s\n\n' third_party/snappy/LICENSE
    cat "$duckdb/third_party/snappy/LICENSE"
    printf '\nFiles: %s\n\n' third_party/snappy/snappy-internal.h
    sed -n 1,29p "$duckdb/third_party/snappy/snappy-internal.h"
    printf '\nFiles: %s\n\n' third_party/snappy/snappy-sinksource.cc
    sed -n 1,27p "$duckdb/third_party/snappy/snappy-sinksource.cc"
    printf '\nFiles: %s\n\n' third_party/snappy/snappy-stubs-internal.h
    sed -n 1,29p "$duckdb/third_party/snappy/snappy-stubs-internal.h"
    printf '\nFiles: %s\n\n' third_party/snappy/snappy-stubs-public.h
    sed -n 1,33p "$duckdb/third_party/snappy/snappy-stubs-public.h"
    printf '\nFiles: %s\n\n' third_party/snappy/snappy.cc
    sed -n 1,27p "$duckdb/third_party/snappy/snappy.cc"
    printf '\nFiles: %s\n\n' third_party/snappy/snappy.h
    sed -n 1,37p "$duckdb/third_party/snappy/snappy.h"
} > /licenses/snappy/copyright

# yyjson
{
    printf '\nFiles: %s\n\n' third_party/yyjson/LICENSE
    cat "$duckdb/third_party/yyjson/LICENSE"
    printf '\nFiles: %s\n\n' third_party/yyjson/include/yyjson.hpp
    sed -n 1,21p "$duckdb/third_party/yyjson/include/yyjson.hpp"
    printf '\nFiles: %s\n\n' third_party/yyjson/yyjson.cpp
    sed -n 1,21p "$duckdb/third_party/yyjson/yyjson.cpp"
} > /licenses/yyjson/copyright

# zstd
{
    printf '\nFiles: %s\n\n' third_party/zstd/LICENSE
    cat "$duckdb/third_party/zstd/LICENSE"
    printf '\nFiles: %s\n\n' third_party/zstd/common/debug.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/common/debug.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/common/entropy_common.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/common/entropy_common.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/common/error_private.cpp
    sed -n 1,9p "$duckdb/third_party/zstd/common/error_private.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/common/fse_decompress.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/common/fse_decompress.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/common/threading.cpp
    sed -n 1,12p "$duckdb/third_party/zstd/common/threading.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/common/xxhash.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/common/xxhash.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/compress/fse_compress.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/compress/fse_compress.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/compress/hist.cpp
    sed -n 1,14p "$duckdb/third_party/zstd/compress/hist.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/compress/huf_compress.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/compress/huf_compress.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/decompress/huf_decompress.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/decompress/huf_decompress.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/dict/divsufsort.cpp
    sed -n 1,25p "$duckdb/third_party/zstd/dict/divsufsort.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/include/zstd/common/bitstream.h
    sed -n 1,13p "$duckdb/third_party/zstd/include/zstd/common/bitstream.h"
    printf '\nFiles: %s\n\n' third_party/zstd/include/zstd/common/fse.h
    sed -n 1,13p "$duckdb/third_party/zstd/include/zstd/common/fse.h"
    printf '\nFiles: %s\n\n' third_party/zstd/include/zstd/common/huf.h
    sed -n 1,13p "$duckdb/third_party/zstd/include/zstd/common/huf.h"
    printf '\nFiles: %s\n\n' third_party/zstd/include/zstd/common/xxhash.hpp
    sed -n 1,13p "$duckdb/third_party/zstd/include/zstd/common/xxhash.hpp"
    printf '\nFiles: %s\n\n' third_party/zstd/include/zstd/dict/divsufsort.h
    sed -n 1,25p "$duckdb/third_party/zstd/include/zstd/dict/divsufsort.h"
} > /licenses/zstd/copyright

# xxhash
{
    printf '\nFiles: %s\n\n' third_party/zstd/common/xxhash.cpp
    sed -n 1,13p "$duckdb/third_party/zstd/common/xxhash.cpp"
    printf '\nFiles: %s\n\n' third_party/zstd/include/zstd/common/xxhash.hpp
    sed -n 1,13p "$duckdb/third_party/zstd/include/zstd/common/xxhash.hpp"
} > /licenses/xxhash/copyright
