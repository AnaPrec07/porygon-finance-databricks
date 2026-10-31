"""Bronze: ingest statement files with Auto Loader as binary (parsing happens in silver, slice 2).

Runs inside a Lakeflow Spark Declarative Pipeline. Verify the `pyspark.pipelines` import and
file-events options against the current runtime when first deploying (see docs/open-questions.md).
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F

from porygon.paths import USER_ID_REGEX

CATALOG = spark.conf.get("porygon.catalog")  # type: ignore[name-defined]  # noqa: F821
BRONZE = spark.conf.get("porygon.schema.bronze")  # type: ignore[name-defined]  # noqa: F821
OPS = spark.conf.get("porygon.schema.ops")  # type: ignore[name-defined]  # noqa: F821
LANDING = spark.conf.get("porygon.landing_path")  # type: ignore[name-defined]  # noqa: F821


@dp.table(
    name=f"{CATALOG}.{BRONZE}.statement_files",
    comment="Raw statement files (binary) as landed. Contains financial data; owner-only.",
    cluster_by=["user_id"],
    table_properties={"sensitivity": "high", "layer": "bronze", "delta.enableDeletionVectors": "true"},
)
@dp.expect("path_has_user_prefix", "user_id IS NOT NULL")
@dp.expect_or_fail("content_not_null", "content IS NOT NULL")
def statement_files():
    return (
        spark.readStream.format("cloudFiles")  # type: ignore[name-defined]  # noqa: F821
        .option("cloudFiles.format", "binaryFile")
        .option("cloudFiles.useManagedFileEvents", "true")
        .load(LANDING)
        .select(
            F.col("_metadata.file_path").alias("source_path"),
            F.col("_metadata.file_name").alias("file_name"),
            F.col("_metadata.file_size").alias("file_size"),
            F.col("_metadata.file_modification_time").alias("file_modified_at"),
            F.nullif(F.regexp_extract("_metadata.file_path", USER_ID_REGEX, 1), F.lit("")).alias("user_id"),
            F.col("content"),
            F.current_timestamp().alias("ingested_at"),
        )
    )


@dp.materialized_view(
    name=f"{CATALOG}.{OPS}.quarantine_files",
    comment="Landed files that could not be attributed to a user. Reason codes only; no content, no paths.",
)
def quarantine_files():
    bronze = spark.read.table(f"{CATALOG}.{BRONZE}.statement_files")  # type: ignore[name-defined]  # noqa: F821
    return bronze.where("user_id IS NULL").select(
        F.sha2("source_path", 256).alias("file_path_hash"),
        F.lit("NO_USER_PREFIX").alias("reason"),
        F.col("file_size"),
        F.col("ingested_at"),
    )
