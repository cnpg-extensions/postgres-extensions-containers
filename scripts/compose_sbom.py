#!/usr/bin/env python3
"""See README.md#sbom-scope for the composition rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence


EXTENSION_PACKAGE_ID = "SPDXRef-Package-extension-payload"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def checksum_key(algorithm: str, value: str) -> tuple[str, str]:
    return algorithm.lower(), value.lower()


def final_files(document: dict[str, Any], path: Path) -> list[dict[str, str]]:
    """Return final file names and checksums from a BuildKit attestation."""

    files: list[dict[str, str]] = []
    for subject in document["subject"]:
        name = subject["name"]
        if name.startswith("pkg:"):
            raise ValueError(
                f"{path}: subject {name!r} is an image subject; use a local-export SBOM"
            )
        files.append({
            "name": name.lstrip("/"),
            "algorithm": "sha256",
            "value": subject["digest"]["sha256"],
        })
    if not files:
        raise ValueError(f"{path}: final image has no file subjects")
    return files


def path_score(candidate: str, final_name: str) -> tuple[int, int]:
    """Prefer an exact path, then the longest shared path suffix."""

    candidate_parts = tuple(part for part in candidate.lstrip("/").split("/") if part)
    final_parts = tuple(part for part in final_name.lstrip("/").split("/") if part)
    common_suffix = 0
    for candidate_part, final_part in zip(reversed(candidate_parts), reversed(final_parts)):
        if candidate_part != final_part:
            break
        common_suffix += 1
    return common_suffix, int(candidate_parts == final_parts)


def file_id(name: str, algorithm: str, value: str) -> str:
    identity = f"{name}\0{algorithm.lower()}:{value.lower()}".encode()
    return f"SPDXRef-File-final-{hashlib.sha256(identity).hexdigest()[:24]}"


def compose(builder_document: dict[str, Any], *,
            extension_name: str,
            builder_path: Path = Path("builder"),
            ) -> dict[str, Any]:
    """Return a raw SPDX predicate composed from a builder attestation."""

    builder = builder_document["predicate"]
    final = final_files(builder_document, builder_path)
    builder_records = builder["files"]
    relationships = builder["relationships"]
    packages = builder["packages"]

    builder_packages = {
        package["SPDXID"]: package
        for package in packages
        if package.get("primaryPackagePurpose") != "FILE"
    }

    all_package_ids = {package["SPDXID"] for package in packages}
    package_ids = set(builder_packages)
    package_ids_by_name: defaultdict[str, set[str]] = defaultdict(set)
    for package_id, package in builder_packages.items():
        package_ids_by_name[package["name"]].add(package_id)
    retained_package_ids: set[str] = set()
    owners_by_source_file: defaultdict[str, set[str]] = defaultdict(set)
    for relationship in relationships:
        if relationship["relationshipType"] != "CONTAINS":
            continue
        package_id = relationship["spdxElementId"]
        source_file_id = relationship["relatedSpdxElement"]
        if package_id in package_ids:
            owners_by_source_file[source_file_id].add(package_id)

    by_checksum: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    all_file_ids = {record["SPDXID"] for record in builder_records}
    for record in builder_records:
        for checksum in record["checksums"]:
            by_checksum[checksum_key(
                checksum["algorithm"], checksum["checksumValue"]
            )].append(record)

    composed_files: list[dict[str, Any]] = []
    source_to_final: defaultdict[str, set[str]] = defaultdict(set)
    direct_final_owners: defaultdict[str, set[str]] = defaultdict(set)
    final_ids: set[str] = set()

    def add_synthetic_file(record: dict[str, str], owner: str | None = None) -> None:
        output_record = {
            "SPDXID": file_id(record["name"], record["algorithm"], record["value"]),
            "checksums": [{
                "algorithm": record["algorithm"].upper(),
                "checksumValue": record["value"],
            }],
            "copyrightText": "NOASSERTION",
            "fileName": record["name"],
            "licenseConcluded": "NOASSERTION",
            "licenseInfoInFiles": ["NOASSERTION"],
        }
        composed_files.append(output_record)
        final_ids.add(output_record["SPDXID"])
        if owner is not None:
            retained_package_ids.add(owner)
            direct_final_owners[output_record["SPDXID"]].add(owner)

    for final_record in final:
        final_name = final_record["name"].lstrip("/")
        license_parts = final_name.split("/", 2)
        if license_parts[0] == "licenses" and len(license_parts) > 1:
            owners = package_ids_by_name.get(license_parts[1], set())
            add_synthetic_file(final_record, next(iter(owners)) if len(owners) == 1 else None)
            continue

        candidates = by_checksum.get(
            checksum_key(final_record["algorithm"], final_record["value"]), []
        )
        if not candidates:
            add_synthetic_file(final_record)
            continue

        owned_candidates = [
            record for record in candidates if record["SPDXID"] in owners_by_source_file
        ]
        candidates = owned_candidates or candidates
        best_score = max(path_score(record["fileName"], final_name) for record in candidates)
        selected = [
            record for record in candidates
            if path_score(record["fileName"], final_name) == best_score
        ]
        selected.sort(key=lambda record: record["SPDXID"])
        source_names = {record["fileName"].lstrip("/") for record in selected}
        if len(source_names) > 1:
            add_synthetic_file(final_record)
            continue

        source = selected[0]
        new_id = file_id(final_record["name"], final_record["algorithm"], final_record["value"])
        output_record = source.copy()
        output_record["SPDXID"] = new_id
        output_record["fileName"] = final_record["name"]
        composed_files.append(output_record)
        final_ids.add(new_id)
        for record in selected:
            source_to_final[record["SPDXID"]].add(new_id)

    owned_final_ids: set[str] = set(direct_final_owners)
    for source_file_id, package_ids_for_file in owners_by_source_file.items():
        final_ids_for_source = source_to_final.get(source_file_id)
        if not final_ids_for_source:
            continue
        retained_package_ids.update(package_ids_for_file)
        owned_final_ids.update(final_ids_for_source)

    extension_file_ids = final_ids - owned_final_ids

    if extension_file_ids:
        retained_package_ids.add(EXTENSION_PACKAGE_ID)

    composed_relationships: list[dict[str, Any]] = []
    seen_relationships: set[str] = set()
    for relationship in relationships:
        element_id = relationship["spdxElementId"]
        related_id = relationship["relatedSpdxElement"]
        if (
            (element_id in all_file_ids and element_id not in source_to_final)
            or (related_id in all_file_ids and related_id not in source_to_final)
        ):
            continue
        if (
            (element_id in all_package_ids and element_id not in retained_package_ids)
            or (related_id in all_package_ids and related_id not in retained_package_ids)
        ):
            continue
        if element_id not in source_to_final and related_id not in source_to_final:
            composed_relationships.append(relationship.copy())
            continue

        element_ids = source_to_final.get(element_id, {element_id})
        related_ids = source_to_final.get(related_id, {related_id})
        for new_element_id in element_ids:
            for new_related_id in related_ids:
                replacement = relationship.copy()
                replacement["spdxElementId"] = new_element_id
                replacement["relatedSpdxElement"] = new_related_id
                identity = json.dumps(replacement, sort_keys=True, separators=(",", ":"))
                if identity not in seen_relationships:
                    seen_relationships.add(identity)
                    composed_relationships.append(replacement)

    composed_relationships.extend(
        {
            "spdxElementId": package_id,
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": file_id_value,
        }
        for file_id_value, package_ids_for_file in direct_final_owners.items()
        for package_id in sorted(package_ids_for_file)
    )

    output = builder.copy()
    output["packages"] = [
        package for package in packages
        if package["SPDXID"] in retained_package_ids
    ]
    if extension_file_ids:
        output["packages"].append({
            "SPDXID": EXTENSION_PACKAGE_ID,
            "copyrightText": "NOASSERTION",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "name": f"{extension_name}-extension-artifacts",
            "supplier": "NOASSERTION",
            "versionInfo": "NOASSERTION",
        })
    output["files"] = composed_files
    output["relationships"] = composed_relationships
    described_ids = {
        relationship["relatedSpdxElement"]
        for relationship in composed_relationships
        if relationship.get("spdxElementId") == output["SPDXID"]
        and relationship.get("relationshipType") == "DESCRIBES"
    }
    for package_id in sorted(retained_package_ids):
        if package_id not in described_ids:
            output["relationships"].append({
                "spdxElementId": output["SPDXID"],
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": package_id,
            })
    if extension_file_ids:
        output["relationships"].extend(
            {
                "spdxElementId": EXTENSION_PACKAGE_ID,
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": file_id_value,
            }
            for file_id_value in sorted(extension_file_ids)
        )
    return output


def aggregate(
    composed_documents: Sequence[tuple[str, dict[str, Any]]],
    *,
    extension_name: str,
) -> dict[str, Any]:
    """Merge composed SPDX documents into one multi-platform document.

    The aggregate intentionally treats platform-specific entities as separate
    inputs, while deduplicating identical package and file records. This keeps
    the document useful to generic SPDX consumers without claiming that every
    package is present on every platform.
    """

    if not composed_documents:
        raise ValueError("aggregate requires at least one composed SPDX document")

    if any(not isinstance(platform, str) or not platform for platform, _ in composed_documents):
        raise ValueError("aggregate platforms must be non-empty strings")
    if len({platform for platform, _ in composed_documents}) != len(composed_documents):
        raise ValueError("aggregate platforms must be unique")
    ordered_documents = sorted(composed_documents, key=lambda item: item[0])
    output = deepcopy(ordered_documents[0][1])
    output["name"] = f"{extension_name}-multi-platform-sbom"
    output["packages"] = []
    output["files"] = []
    output["relationships"] = []
    output.pop("annotations", None)

    entities: dict[tuple[str, str], str] = {}
    used_ids: set[str] = set()
    relationships: dict[str, dict[str, Any]] = {}
    annotations: dict[str, dict[str, Any]] = {}

    def entity_key(entity: dict[str, Any]) -> str:
        return json.dumps(
            {key: value for key, value in entity.items() if key != "SPDXID"},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def aggregate_id(platform: str, original_id: str) -> str:
        platform_id = re.sub(r"[^A-Za-z0-9.-]+", "-", platform).strip("-")
        original_suffix = original_id.removeprefix("SPDXRef-")
        original_suffix = re.sub(r"[^A-Za-z0-9.-]+", "-", original_suffix).strip("-")
        candidate = f"SPDXRef-{platform_id}-{original_suffix}"
        suffix = 2
        while candidate in used_ids:
            candidate = f"SPDXRef-{platform_id}-{original_suffix}-{suffix}"
            suffix += 1
        return candidate

    for platform, document in ordered_documents:
        id_map = {"SPDXRef-DOCUMENT": "SPDXRef-DOCUMENT"}
        for entity_type in ("packages", "files"):
            records = document.get(entity_type, [])
            for record in records:
                original_id = record["SPDXID"]
                key = (entity_type, entity_key(record))
                if key not in entities:
                    new_id = aggregate_id(platform, original_id)
                    entities[key] = new_id
                    used_ids.add(new_id)
                    merged_record = deepcopy(record)
                    merged_record["SPDXID"] = new_id
                    output[entity_type].append(merged_record)
                id_map[original_id] = entities[key]

        def map_id(identifier: str) -> str:
            if identifier in id_map:
                return id_map[identifier]
            if identifier == "SPDXRef-DOCUMENT":
                return identifier
            mapped = aggregate_id(platform, identifier)
            used_ids.add(mapped)
            id_map[identifier] = mapped
            return mapped

        for relationship in document.get("relationships", []):
            mapped = deepcopy(relationship)
            mapped["spdxElementId"] = map_id(relationship["spdxElementId"])
            mapped["relatedSpdxElement"] = map_id(relationship["relatedSpdxElement"])
            identity = json.dumps(mapped, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            relationships[identity] = mapped

        for annotation in document.get("annotations", []):
            mapped = deepcopy(annotation)
            if isinstance(mapped.get("spdxElementId"), str):
                mapped["spdxElementId"] = map_id(mapped["spdxElementId"])
            identity = json.dumps(mapped, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            annotations[identity] = mapped

    output["packages"].sort(key=lambda record: record["SPDXID"])
    output["files"].sort(key=lambda record: record["SPDXID"])
    output["relationships"] = [relationships[key] for key in sorted(relationships)]
    if annotations:
        output["annotations"] = [annotations[key] for key in sorted(annotations)]
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose final-image package owners and files from builder SPDX data"
    )
    parser.add_argument(
        "--builder-sbom",
        type=Path,
        action="append",
        help="Builder-stage SBOM, repeat once per aggregate platform",
    )
    parser.add_argument(
        "--aggregate-from",
        type=Path,
        action="append",
        help="Composed SPDX document to include in a multi-platform aggregate",
    )
    parser.add_argument(
        "--platform",
        action="append",
        help="Platform corresponding to each --aggregate-from input",
    )
    parser.add_argument("--extension-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    builder_sboms = args.builder_sbom or []
    aggregate_inputs = args.aggregate_from or []
    platforms = args.platform or []
    if aggregate_inputs:
        if len(aggregate_inputs) != len(platforms):
            parser.error("--aggregate-from and --platform must have the same number of values")
        output = aggregate(
            [
                (platform, read_json(path))
                for platform, path in zip(platforms, aggregate_inputs)
            ],
            extension_name=args.extension_name,
        )
    else:
        if len(builder_sboms) != 1:
            parser.error("single-document mode requires exactly one --builder-sbom")
        output = compose(
            read_json(builder_sboms[0]),
            extension_name=args.extension_name,
            builder_path=builder_sboms[0],
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(
        f"composed {len(output['packages'])} packages, "
        f"{len(output['files'])} final files, "
        f"{len(output['relationships'])} relationships",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
