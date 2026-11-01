"""One-time, admin-run: IAM role, UC storage credential and external location for the landing bucket.

Run once per environment from a machine with AWS credentials (IAM permissions) and Databricks auth
(env vars or a profile) that can create storage credentials / external locations:

    pip install boto3 databricks-sdk
    set -a; source infra/.env; set +a      # copy infra/.env.example to infra/.env first (git-ignored)
    python infra/bootstrap_landing_zone.py

NOT idempotent: re-running fails at `create_policy` / `create_role` because they already exist.
TODO(security): the permissions policy has no KMS statement. The spec requires SSE-KMS, so add
kms:Decrypt / kms:GenerateDataKey on the bucket's CMK (and allow this role in the key policy) once
the CMK exists. See docs/adr/0002-privacy-and-access-model.md.
"""

import json
import os
import time

import boto3
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import AwsIamRoleRequest, PermissionsChange, Privilege, SecurableType


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name} (see infra/.env.example)")
    return value


ACCOUNT = _env("AWS_ACCOUNT_ID")
BUCKET = _env("LANDING_BUCKET")
ROLE = os.environ.get("UC_ROLE_NAME", "databricks-uc-landing-zone")
UC_MASTER = _env("UC_MASTER_ROLE_ARN")  # Databricks' Unity Catalog master role for your region
GRANTEE_GROUP = os.environ.get("LANDING_GRANTEE_GROUP", "data-engineers")
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/{ROLE}"

iam = boto3.client("iam")
w = WorkspaceClient()  # auth via env vars or a Databricks profile


def trust(principals, external_id):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": principals},
                    "Action": "sts:AssumeRole",
                    "Condition": {"StringEquals": {"sts:ExternalId": external_id}},
                }
            ],
        }
    )


# 1. Permissions policy
policy = iam.create_policy(
    PolicyName=f"{ROLE}-policy",
    PolicyDocument=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Resource": [f"arn:aws:s3:::{BUCKET}", f"arn:aws:s3:::{BUCKET}/*"],
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket",
                        "s3:GetBucketLocation",
                        "s3:ListBucketMultipartUploads",
                        "s3:ListMultipartUploadParts",
                        "s3:AbortMultipartUpload",
                    ],
                },
                {"Effect": "Allow", "Action": "sts:AssumeRole", "Resource": ROLE_ARN},
            ],
        }
    ),
)

# 2. Role with a placeholder external ID, then attach the policy
iam.create_role(RoleName=ROLE, AssumeRolePolicyDocument=trust(UC_MASTER, "0000"))
iam.attach_role_policy(RoleName=ROLE, PolicyArn=policy["Policy"]["Arn"])
time.sleep(15)  # IAM changes take a moment to propagate

# 3. Databricks storage credential; it returns the real external ID
cred = w.storage_credentials.create(
    name="landing-zone-cred", aws_iam_role=AwsIamRoleRequest(role_arn=ROLE_ARN)
)
external_id = cred.aws_iam_role.external_id

# 4. Fix the trust policy: real external ID plus self-assume
iam.update_assume_role_policy(RoleName=ROLE, PolicyDocument=trust([UC_MASTER, ROLE_ARN], external_id))
time.sleep(15)

# 5. External location and grants (to a group, not to you)
w.external_locations.create(
    name="porygon-landing-zone", url=f"s3://{BUCKET}", credential_name="landing-zone-cred"
)
w.grants.update(
    securable_type=SecurableType.EXTERNAL_LOCATION,
    full_name="porygon-landing-zone",
    changes=[PermissionsChange(principal=GRANTEE_GROUP, add=[Privilege.READ_FILES, Privilege.WRITE_FILES])],
)
