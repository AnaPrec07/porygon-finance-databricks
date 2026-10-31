# ADR 0002: Privacy and access model
Status: accepted

- Bronze: pipeline SP only. Silver/gold: pipeline SP + API SP (read). Shared: founder group (read). Ops: data-admin group (read; reason codes only, no PII).
- S3 and UC managed storage use a customer-managed KMS key whose policy allows only the pipeline and API service principals.
- Residual risk: a cloud/metastore root admin could change a key policy or grant themselves access. Mitigation: metastore admin is a group used for break-glass only, and `system.access.audit` alerts on non-service-principal reads (slice 6).
- Row filters / column masks are added in slice 4+ as defense in depth on top of the API.
