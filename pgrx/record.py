#!/usr/bin/env python3
"""Carry native build digests between jobs in the same prepared workflow run."""

import json

from prepare import digest, save
from workflow import source_digest


def load_preparation(directory):
    preparation = json.loads((directory / "preparation.json").read_text())
    expected = preparation.pop("preparation_sha256")
    if digest(preparation) != expected:
        raise ValueError("preparation checksum mismatch")
    preparation["preparation_sha256"] = expected
    if preparation["workspace_sha256"] != source_digest():
        raise ValueError("workspace differs from preparation")
    return preparation


def expected_row(preparation, row_id):
    rows = [r for r in preparation["rows"] if r["id"] == row_id]
    if len(rows) != 1:
        raise ValueError("unexpected platform record")
    return rows[0]


def capture(preparation_dir, row_id, index_digest, output):
    preparation = load_preparation(preparation_dir)
    row = expected_row(preparation, row_id)
    if output.exists():
        raise ValueError("fresh record output required")
    output.mkdir(parents=True)
    repository = row["staging"].rsplit(":", 1)[0]
    image = repository + "@" + index_digest
    record = {
        "schema_version": 1,
        "row": row,
        "preparation_sha256": preparation["preparation_sha256"],
        "run_id": preparation["run_id"],
        "workspace_sha256": preparation["workspace_sha256"],
        "git_sha": preparation["git_sha"],
        "timestamp": preparation["timestamp"],
        "generator": preparation["generator"],
        "image": image,
        "index_digest": index_digest,
    }
    save(output / "record.json", record)
    return record


def validate_record(preparation, row, artifact):
    record = json.loads((artifact / "record.json").read_text())
    if (
        record.get("schema_version") != 1
        or record["git_sha"] != preparation["git_sha"]
        or record["timestamp"] != preparation["timestamp"]
        or record["row"] != row
        or record["preparation_sha256"] != preparation["preparation_sha256"]
        or record["run_id"] != preparation["run_id"]
        or record["workspace_sha256"] != preparation["workspace_sha256"]
        or record["generator"] != preparation["generator"]
    ):
        raise ValueError("record does not match independent preparation")
    if (
        record["image"]
        != row["staging"].rsplit(":", 1)[0] + "@" + record["index_digest"]
    ):
        raise ValueError("unexpected staging repository")
    return record
