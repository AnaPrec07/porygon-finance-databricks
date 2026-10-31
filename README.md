# Porygon Finance Pilot - Databricks data platform

Databricks Asset Bundle for ingestion -> bronze -> silver -> gold -> shared. See `docs/plan.md` (plan), `docs/adr/`, `docs/open-questions.md`.

Status: slice 1 (skeleton). Bronze ingestion + quarantine + post-ingestion file purge exist; parsers, silver and gold come in slice 2.

```bash
pip install -e ".[dev]"      # tooling
ruff check . && mypy src && pytest -q
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

Before first deploy: run `infra/uc_bootstrap.sql` once per environment and replace the `REPLACE` values in `databricks.yml`.
Synthetic data only: never commit real statements.
