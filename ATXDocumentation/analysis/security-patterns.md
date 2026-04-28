# Security Patterns

> Back to: [README](../README.md) | [Code Metrics](code-metrics.md) | [Complexity Analysis](complexity-analysis.md) | [Dependency Analysis](dependency-analysis.md) | [Tech Debt](tech-debt.md)

## IAM Least Privilege Analysis

### Delegation Lambda Role (`rIpamLambdaRoleDelegate`)

**Template:** `vpc-ipam-delegation.yaml`

| Action | Resource | Assessment |
|--------|----------|------------|
| `ec2:EnableIpamOrganizationAdminAccount` | `*` | ⚠️ Wildcard — but EC2 IPAM org-level APIs don't support resource-level permissions |
| `ec2:DisableIpamOrganizationAdminAccount` | `*` | ⚠️ Wildcard — same as above |
| `organizations:RegisterDelegatedAdministrator` | `*` | ⚠️ Wildcard — Organizations APIs don't support resource-level permissions |
| `organizations:DeregisterDelegatedAdministrator` | `*` | ⚠️ Wildcard — same as above |
| `organizations:EnableAWSServiceAccess` | `*` | ⚠️ Wildcard — same as above |
| `iam:CreateServiceLinkedRole` | `*` | ❌ **Should be scoped** to `arn:aws:iam::*:role/aws-service-role/ipam.amazonaws.com/*` |

**Managed Policy:** `AWSLambdaBasicExecutionRole` — Provides CloudWatch Logs permissions. Appropriate for Lambda.

**Findings:**
- Most actions legitimately require `Resource: "*"` due to AWS API limitations
- `iam:CreateServiceLinkedRole` should be scoped to the IPAM service-linked role ARN
- No `Condition` keys used to further restrict permissions

### Pool Lookup Lambda Role (`rIpamLambdaRoleGetPoolId`)

**Template:** `custom-vpc.yaml`

| Action | Resource | Assessment |
|--------|----------|------------|
| `ec2:DescribeIpamPools` | `*` | ⚠️ Wildcard — but EC2 Describe APIs don't support resource-level permissions |

**Managed Policy:** `AWSLambdaBasicExecutionRole`

**Findings:**
- This is a read-only role with minimal permissions
- `ec2:DescribeIpamPools` legitimately requires `Resource: "*"`
- This role follows least privilege principles well

## Lambda Execution Role Patterns

| Aspect | Delegation Lambda | Pool Lookup Lambda |
|--------|------------------|--------------------|
| Trust Policy | `lambda.amazonaws.com` | `lambda.amazonaws.com` |
| Managed Policy | `AWSLambdaBasicExecutionRole` | `AWSLambdaBasicExecutionRole` |
| Custom Policy | 6 actions, Resource: `*` | 1 action, Resource: `*` |
| Path | `/` | `/` |
| Permission Scope | Write (enable/disable delegation) | Read-only (describe pools) |

## CloudFormation Parameter Validation

### Input Validation Patterns

| Parameter | Validation Type | Pattern/Values | Effectiveness |
|-----------|----------------|----------------|---------------|
| `pNetworkAccountId` | AllowedPattern + Length | `^[0-9]{12}$`, 12 chars | ✅ Strong |
| `pOrganizationId` | AllowedPattern + Length | `^[o][\-][a-z0-9]{10}$`, 12 chars | ✅ Strong |
| `pManagementAccountId` | AllowedPattern + Length | `^[0-9]{12}$`, 12 chars | ✅ Strong |
| `pTagEnvironment` | AllowedValues | Enumerated list | ✅ Strong |
| `pVpcSize` | AllowedValues | `Small/Medium/Large` | ✅ Strong |
| `pLambdaLogGroupRetention` | AllowedValues | Enumerated integers | ✅ Strong |
| `pOperatingRegionList` | None | List\<String\> | ❌ No validation |
| `pMainPoolCidrIpv4List` | None | List\<String\> | ❌ No validation |
| `pProdPoolCidrIpv4List` | None | List\<String\> | ❌ No validation |
| `pUatPoolCidrIpv4List` | None | List\<String\> | ❌ No validation |
| `pDevPoolCidrIpv4List` | None | List\<String\> | ❌ No validation |

**Finding:** List\<String\> parameters (regions and CIDRs) have no validation. Malformed inputs could cause deployment failures or unexpected behavior. CloudFormation does not support `AllowedPattern` for `List<String>` types, so validation would need to be handled via a Custom Resource or CloudFormation Guard rules.

## RAM Sharing Security

**Resource:** `rRamShareIpamEnvironmentPoolIpv4` in `vpc-ipam-pools.yaml`

| Setting | Value | Assessment |
|---------|-------|------------|
| `AllowExternalPrincipals` | `false` | ✅ Prevents sharing outside the Organization |
| Principal | Organization ARN | ✅ Scoped to the specific Organization |
| Permission | `AWSRAMDefaultPermissionsIpamPool` | ✅ Uses AWS managed permission |

**Finding:** RAM sharing is properly configured to restrict access within the Organization. External principals are explicitly denied.

## Encryption Analysis

| Resource | Encryption | Assessment |
|----------|-----------|------------|
| CloudWatch Log Groups | Not configured | ⚠️ No KMS encryption |
| Lambda Environment Variables | Default AWS encryption | ✅ Encrypted at rest by default |
| IPAM data | Managed by AWS | ✅ AWS-managed encryption |
| VPC resources | N/A | N/A (networking resources) |

**Finding:** CloudWatch Log Groups should use customer-managed KMS keys for sensitive environments. Lambda environment variables are encrypted by default using AWS-managed keys; customer-managed KMS keys can be configured for additional control.

## Network Security

| Resource | Configuration | Assessment |
|----------|--------------|------------|
| VPC | DNS support + hostnames enabled | ✅ Standard |
| Public subnets | IGW route | ✅ Expected for public tier |
| Hybrid subnets | NAT Gateway route | ✅ Outbound-only internet |
| Private subnets | NAT Gateway route | ⚠️ Same as hybrid — consider removing NAT for true private |
| NAT Gateways | 3 (one per AZ) | ✅ HA pattern |
| VPC Flow Logs | Not configured | ❌ Missing — recommended for security monitoring |

**Finding:** Private subnets route through NAT Gateways, which provides outbound internet access. If truly private (no internet) subnets are needed, the NAT Gateway routes should be removed. VPC Flow Logs are not configured but are recommended for security and compliance.

---

> See also: [Technical Debt: Remediation Plan](../technical-debt/remediation-plan.md) | [Behavior: Error Handling](../behavior/error-handling.md)
