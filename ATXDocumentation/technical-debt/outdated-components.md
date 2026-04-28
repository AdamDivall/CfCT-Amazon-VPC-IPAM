# Outdated Components Analysis

> Back to: [Technical Debt Report](../technical-debt-report.md) | [Summary](summary.md) | [Maintenance Burden](maintenance-burden.md) | [Remediation Plan](remediation-plan.md)

## Python 3.9 Lambda Runtime — **High Severity**

### Current State

Both Lambda functions in the project use `Runtime: python3.9`:

- **`vpc-ipam-delegation.yaml`** → `rIpamLambdaDelegate` (line ~126)
- **`custom-vpc.yaml`** → `rIpamLambdaGetPoolId` (line ~120)

### EOL Timeline

| Milestone | Date |
|-----------|------|
| Python 3.9 release | October 2020 |
| Python 3.9 end-of-life (CPython) | October 2025 |
| AWS Lambda deprecation (Phase 1 — no new functions) | Expected shortly after CPython EOL |
| AWS Lambda deprecation (Phase 2 — no updates) | Expected within months of Phase 1 |

### Impact

- **Deployment Risk:** After AWS deprecates the runtime, CloudFormation stack create/update operations that include these Lambda functions will fail.
- **Security Risk:** No security patches will be backported to Python 3.9 after EOL.
- **Compliance Risk:** Running EOL software may violate organizational compliance policies.

### Upgrade Path

The Lambda functions use only:
- `boto3` (bundled with Lambda runtime)
- `cfnresponse` (bundled with Lambda runtime for CloudFormation)
- `os` (standard library)
- `botocore.exceptions.ClientError` (bundled with Lambda runtime)

No third-party dependencies or Python 3.9-specific features are used. Upgrade to `python3.12` or `python3.13` is expected to be a zero-change migration — only the `Runtime` property needs to be updated in both CloudFormation templates.

### Recommended Target

| Target | Status | Rationale |
|--------|--------|-----------|
| `python3.12` | ✅ Recommended | LTS, well-established, broad ecosystem support |
| `python3.13` | ✅ Alternative | Latest stable, longest support window |
| `python3.11` | ⚠️ Acceptable | Shorter remaining support window |

## boto3 — No Pinned Version — **Low Severity**

### Current State

Both Lambda functions import `boto3` without specifying a version. They rely on the version bundled with the AWS Lambda runtime. This means the exact boto3 version varies depending on when the Lambda execution environment was provisioned.

### Impact

- Minor risk of API behavior changes between boto3 versions
- Generally acceptable for inline CloudFormation Lambda functions
- No action required unless specific API behavior pinning is needed

### Recommendation

For production workloads, consider using Lambda Layers with a pinned boto3 version, or packaging boto3 as part of the deployment artifact.

## CloudFormation Template Format — **No Issue**

`AWSTemplateFormatVersion: 2010-09-09` is the only supported version and is not subject to deprecation.

## AWS Service APIs Used

All AWS service APIs used in this project are current and not deprecated:

| API | Status |
|-----|--------|
| `ec2:EnableIpamOrganizationAdminAccount` | Current |
| `ec2:DisableIpamOrganizationAdminAccount` | Current |
| `ec2:DescribeIpamPools` | Current |
| `organizations:RegisterDelegatedAdministrator` | Current |
| `organizations:DeregisterDelegatedAdministrator` | Current |
| `organizations:EnableAWSServiceAccess` | Current |
| `iam:CreateServiceLinkedRole` | Current |

---

> See also: [Remediation Plan](remediation-plan.md) | [Analysis Tech Debt](../analysis/tech-debt.md)
