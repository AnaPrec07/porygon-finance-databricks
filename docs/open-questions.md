# Open questions and assumptions
Decided by the owner: Lakebase for serving and user corrections; async import (~2-3 min); explicit delete step instead of `cleanSource`; Banco General first; workspace per env for staging/prod (assumed from "yes").

| # | Question | Assumption (configurable) |
|---|---|---|
| 1 | Bank export formats (headers) | Owner will supply later. Per-bank config; XLSX/CSV only; no PDF. |
| 2 | Accuracy tolerance | Month = bank-stated transaction date. |
| 3 | Shared-result payload | `(pseudonym, month, savings_rate)`; min cohort size 5. |
| 4 | Category list | Placeholder reference table; needs founder approval. |
| 5 | Savings-transfer detection | Config keywords plus user tag. |
| 6 | No salary detected | Flag `income_missing`; use income override. |
| 7 | Retention numbers | VACUUM 0-24 h after deletion; no S3 versioning on landing. |
| 8 | Founder's existing Databricks integrations | None assumed. |
| 9 | Verify on first deploy | `pyspark.pipelines` import, `cloudFiles.useManagedFileEvents`, wheel path in pipeline `environment.dependencies`, volume `storage_location` in bundle, `bundle validate` (CLI was not available when this was written). |
| 10 | AWS account/region/workspace IDs and bucket names | Placeholders marked `REPLACE` in `databricks.yml`. |
