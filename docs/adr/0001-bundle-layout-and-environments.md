# ADR 0001: Bundle layout and environments
Status: accepted (pending confirmation of the workspace-per-env cost)

- One bundle; targets `dev` (development mode, per developer), `staging`, `prod` (production mode, `run_as` service principal).
- One catalog per environment; schemas `bronze`, `silver`, `gold`, `shared`, `ops`. Staging and prod live in separate workspaces; dev shares a workspace with a `porygon_dev` catalog.
- Code is a Python package (`src/porygon`) built as a wheel; pipelines and jobs depend on it. Pure logic is unit-tested without Spark.
- Catalog and external location are created once by `infra/uc_bootstrap.sql` (admin-run); everything else is in the bundle.
