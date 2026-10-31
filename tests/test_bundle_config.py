"""Static checks on bundle YAML (cheap guardrails; `databricks bundle validate` runs in CI too)."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_SCHEMAS = ("bronze", "silver", "gold")


def _load(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text())


def test_all_layers_defined() -> None:
    schemas = _load("resources/schemas.yml")["resources"]["schemas"]
    assert set(schemas) == {"bronze", "silver", "gold", "shared", "ops"}


def test_founder_only_reads_shared() -> None:
    schemas = _load("resources/schemas.yml")["resources"]["schemas"]
    for name, schema in schemas.items():
        principals = [g["principal"] for g in schema.get("grants", [])]
        assert ("${var.founder_group}" in principals) == (name == "shared"), name


def test_api_sp_has_no_access_to_bronze() -> None:
    schemas = _load("resources/schemas.yml")["resources"]["schemas"]
    assert all(g["principal"] != "${var.api_sp}" for g in schemas["bronze"]["grants"])


def test_pipeline_is_serverless_and_triggered() -> None:
    pipe = _load("resources/pipelines.yml")["resources"]["pipelines"]["ingest_pipeline"]
    assert pipe["serverless"] is True and pipe["continuous"] is False


def test_prod_runs_as_service_principal() -> None:
    targets = _load("databricks.yml")["targets"]
    for env in ("staging", "prod"):
        assert "service_principal_name" in targets[env]["run_as"]


def test_jobs_are_tagged() -> None:
    job = _load("resources/jobs.yml")["resources"]["jobs"]["ingest_job"]
    assert {"project", "env", "owner"} <= set(job["tags"])
