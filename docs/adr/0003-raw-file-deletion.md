# ADR 0003: Delete raw files with an explicit post-ingestion task
Status: accepted

`cloudFiles.cleanSource` acts after a retention window (DELETE requires more than 7 days) and is documented mainly as a listing-cost optimization. The spec requires deletion after parsing, so the job runs `purge_landed_files` after the pipeline succeeds. It deletes only files whose path exists in `bronze.statement_files`. An S3 lifecycle rule (1 day) on the landing prefix is a backstop (to be added to infra).
Note: bronze stores file content, so deleting the S3 file is not enough; bronze content must be dropped once silver is parsed (slice 2), and the deletion job (slice 5) purges it per user.
