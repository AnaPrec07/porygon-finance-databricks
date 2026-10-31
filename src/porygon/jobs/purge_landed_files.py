"""Delete landed statement files after their content is committed to bronze.

Why not `cloudFiles.cleanSource`? It acts after a retention window (see docs/adr/0003). The spec
requires the raw file to be deleted after parsing, so we delete explicitly, and only files whose
path exists in bronze (never delete something that was not ingested).
"""

from __future__ import annotations

import argparse
import os

from porygon.paths import files_to_purge


def list_landed_files(landing_path: str) -> list[str]:
    found: list[str] = []
    for root, _dirs, files in os.walk(landing_path):
        found.extend(os.path.join(root, name) for name in files)
    return found


def main(argv: list[str] | None = None) -> None:
    from pyspark.sql import SparkSession  # imported lazily: not available in unit tests

    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--bronze-schema", required=True)
    parser.add_argument("--landing-path", required=True)
    args = parser.parse_args(argv)

    spark = SparkSession.builder.getOrCreate()
    rows = spark.table(f"`{args.catalog}`.`{args.bronze_schema}`.statement_files").select("source_path")
    committed = {r["source_path"] for r in rows.collect()}
    to_delete = files_to_purge(list_landed_files(args.landing_path), committed)
    for path in to_delete:
        os.remove(path)
    # Log counts only: never paths or file names (they contain user ids).
    print(f"purged_files={len(to_delete)}")


if __name__ == "__main__":
    main()
