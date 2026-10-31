-- One-time, admin-run setup per environment (replace the <placeholders>). Run as a metastore admin
-- group member, then never again: everything else is deployed by `databricks bundle deploy`.
-- Prereqs (outside SQL): S3 bucket with SSE-KMS CMK, IAM role, and a UC storage credential
-- (<storage_credential>) created by your platform admin. The key policy should allow only the
-- pipeline and API service principals (see docs/adr/0002).
-- NOTE: I have not verified that your CLI version supports a `catalogs` bundle resource; if it does
-- this file can move into resources/.

CREATE EXTERNAL LOCATION IF NOT EXISTS `porygon_<env>_landing`
  URL 's3://<bucket>/landing'
  WITH (STORAGE CREDENTIAL `<storage_credential>`)
  COMMENT 'Statement file landing zone (SSE-KMS). Owned by a group, not an individual.';

CREATE CATALOG IF NOT EXISTS `porygon_<env>`
  COMMENT 'Porygon Finance Pilot data platform (<env>).';

ALTER CATALOG `porygon_<env>` SET OWNER TO `<platform_admins_group>`;
ALTER EXTERNAL LOCATION `porygon_<env>_landing` SET OWNER TO `<platform_admins_group>`;

-- The pipeline SP needs to create schemas/volumes and use the external location.
GRANT USE_CATALOG, CREATE_SCHEMA ON CATALOG `porygon_<env>` TO `<pipeline_sp>`;
GRANT USE_CATALOG ON CATALOG `porygon_<env>` TO `<api_sp>`;
GRANT USE_CATALOG ON CATALOG `porygon_<env>` TO `<founder_group>`;
GRANT CREATE_EXTERNAL_VOLUME, READ_FILES, WRITE_FILES
  ON EXTERNAL LOCATION `porygon_<env>_landing` TO `<pipeline_sp>`;
