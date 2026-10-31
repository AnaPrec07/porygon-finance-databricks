-- One-time, admin-run setup per environment (replace the <placeholders>). Run as a metastore admin
-- group member, then never again: everything else is deployed by `databricks bundle deploy`.
-- Prereqs (outside SQL): S3 bucket with SSE-KMS CMK, IAM role, and a UC storage credential
-- (`landing-zone-cred`, created by infra/bootstrap_landing_zone.py). The key policy should allow only the
-- pipeline and API service principals (see docs/adr/0002).
-- NOTE: I have not verified that your CLI version supports a `catalogs` bundle resource; if it does
-- this file can move into resources/.

-- The external location `porygon-landing-zone` (storage credential `landing-zone-cred`) is created by
-- infra/bootstrap_landing_zone.py; run that first.

CREATE CATALOG IF NOT EXISTS `porygon_<env>`
  COMMENT 'Porygon Finance Pilot data platform (<env>).';

ALTER CATALOG `porygon_<env>` SET OWNER TO `<platform_admins_group>`;
ALTER EXTERNAL LOCATION `porygon-landing-zone` SET OWNER TO `<platform_admins_group>`;

-- The pipeline SP needs to create schemas/volumes and use the external location.
GRANT USE_CATALOG, CREATE_SCHEMA ON CATALOG `porygon_<env>` TO `<pipeline_sp>`;
GRANT USE_CATALOG ON CATALOG `porygon_<env>` TO `<api_sp>`;
GRANT USE_CATALOG ON CATALOG `porygon_<env>` TO `<founder_group>`;
GRANT CREATE_EXTERNAL_VOLUME, READ_FILES, WRITE_FILES
  ON EXTERNAL LOCATION `porygon-landing-zone` TO `<pipeline_sp>`;
