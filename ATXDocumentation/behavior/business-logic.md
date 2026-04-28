> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Business Logic

> Back to: [README](../README.md) | [Workflows](workflows.md) | [Decision Logic](decision-logic.md) | [Error Handling](error-handling.md)

## Overview

The business logic in this project spans three CloudFormation templates and two Lambda functions, implementing an end-to-end IPAM lifecycle from delegation through pool management to VPC provisioning.

---

## 1. IPAM Delegation Enable/Disable Logic

**Source:** `vpc-ipam-delegation.yaml` → `rIpamLambdaDelegate` (inline ZipFile)  
**Also:** `lambda/lambda-vpc-ipam-delegation.py` (duplicate)

### Business Rule: Enable IPAM Delegation

**Trigger:** CloudFormation Custom Resource `Create` or `Update` event  
**Input:** `event['ResourceProperties']['accountid']` (12-digit AWS Account ID)

**Logic:**
1. Call `ec2.enable_ipam_organization_admin_account(DryRun=False, DelegatedAdminAccountId=accountid)`
2. Check `response['Success'] == True`
3. If successful: signal `cfnresponse.SUCCESS`
4. If `ClientError`: print error message, signal `cfnresponse.FAILED`

### Business Rule: Disable IPAM Delegation

**Trigger:** CloudFormation Custom Resource `Delete` event  
**Input:** Same `accountid` from resource properties

**Logic:**
1. Call `ec2.disable_ipam_organization_admin_account(DryRun=False, DelegatedAdminAccountId=accountid)`
2. Check `response['Success'] == True`
3. If successful: signal `cfnresponse.SUCCESS`
4. If `ClientError`: print error message, signal `cfnresponse.FAILED`

### Business Rule: Unknown Request Type

**Trigger:** Any CloudFormation event that is not `Create`, `Update`, or `Delete`  
**Logic:** Signal `cfnresponse.SUCCESS` (no-op passthrough)

---

## 2. IPAM Pool ID Lookup by Environment and Region

**Source:** `custom-vpc.yaml` → `rIpamLambdaGetPoolId` (inline ZipFile)

### Business Rule: Find Matching IPAM Pool

**Trigger:** CloudFormation Custom Resource `Create` event  
**Inputs:**
- `AWS_REGION` environment variable (automatic from Lambda runtime)
- `ENVIRONMENT` environment variable (set from `pTagEnvironment` parameter)

**Logic:**
1. Call `ec2.describe_ipam_pools(DryRun=False, Filters=[{'Name': 'locale', 'Values': [region]}])`
2. If no pools returned (`len(ipam_pool['IpamPools']) == 0`): print warning, default status is `FAILED`
3. For each pool in the response:
   a. Check if pool has `AllocationResourceTags`
   b. For each tag in `AllocationResourceTags`:
      - If `tag['Value'] == environment`: capture `IpamPoolId`, set status to `SUCCESS`, break inner loop
      - Else: print "No IPAM Pools with Allocation Resource Tags that match the Environment"
   c. If pool has empty `AllocationResourceTags`: print "IPAM Pool has no Allocation Resource Tags applied"
4. Send `cfnresponse` with status and `responseData['Data'] = ip_pool_id` (if found)

### Business Rule: Update/Delete No-Op

**Trigger:** CloudFormation Custom Resource `Update` or `Delete` event  
**Logic:** Signal `cfnresponse.SUCCESS` immediately with empty response data (the pool ID only needs to be resolved once at VPC creation time)

---

## 3. VPC CIDR Allocation from IPAM Pools

**Source:** `custom-vpc.yaml` → `rVpc` resource

### Business Rule: VPC Gets CIDR from IPAM

The VPC resource uses IPAM for automatic CIDR allocation instead of specifying a static CIDR:

```yaml
Ipv4IpamPoolId: !GetAtt rCustomGetPoolId.Data    # Pool ID from Lambda lookup
Ipv4NetmaskLength: !FindInMap [mVpcSize, !Ref pVpcSize, VpcCidr]  # /22, /20, or /19
```

IPAM automatically allocates the next available CIDR of the specified netmask length from the matched pool. This ensures non-overlapping IP addresses across all VPCs in the organization.

---

## 4. Subnet CIDR Calculation

**Source:** `custom-vpc.yaml` → Subnet resources

### Business Rule: Fn::Cidr Subnet Division

Each subnet's CIDR is calculated using CloudFormation's `Fn::Cidr` intrinsic function:

```yaml
CidrBlock: !Select [ <index>, !Cidr [ !GetAtt rVpc.CidrBlock, 9, !FindInMap [mVpcSize, !Ref pVpcSize, <tier>Cidr]]]
```

**Subnet Index Mapping:**
| Index | Subnet | Tier |
|-------|--------|------|
| 0 | Public A | Public |
| 1 | Public B | Public |
| 2 | Public C | Public |
| 3 | Hybrid A | Hybrid |
| 4 | Hybrid B | Hybrid |
| 5 | Hybrid C | Hybrid |
| 6 | Private A | Private |
| 7 | Private B | Private |
| 8 | Private C | Private |

**Size Bits per Tier (from `mVpcSize` mapping):**

| VPC Size | Public Bits | Hybrid Bits | Private Bits |
|----------|-------------|-------------|--------------|
| Small | 4 (16 IPs) | 6 (64 IPs) | 6 (64 IPs) |
| Medium | 4 (16 IPs) | 8 (256 IPs) | 8 (256 IPs) |
| Large | 4 (16 IPs) | 9 (512 IPs) | 9 (512 IPs) |

---

## 5. RAM Sharing to Organization

**Source:** `vpc-ipam-pools.yaml` → `rRamShareIpamEnvironmentPoolIpv4`

### Business Rule: Share All Environment Pools

All environment-level IPAM pools are shared to the entire AWS Organization via RAM:

- **Principal:** `arn:aws:organizations::<ManagementAccountId>:organization/<OrganizationId>`
- **AllowExternalPrincipals:** `false` (internal Organization only)
- **Permission:** `AWSRAMDefaultPermissionsIpamPool`
- **Resources:** All 6 environment pools (Region 1: Prod/UAT/Dev + Region 2: Prod/UAT/Dev) plus 3 non-existent Region 3 pools (⚠️ bug)

This enables any member account in the Organization to use the shared IPAM pools for VPC CIDR allocation.

---

## 6. IPAM Pool Hierarchy Configuration

**Source:** `vpc-ipam-pools.yaml`

### Business Rule: Hierarchical Pool Provisioning

The IPAM pools follow a strict hierarchy where each level inherits from the parent:

1. **Top Pool** receives the full CIDR range (3 CIDRs from `pMainPoolCidrIpv4List`)
2. **Regional Pools** source from the Top Pool and receive a single CIDR per region
3. **Environment Pools** source from their Regional Pool, are locale-bound, and tagged with the environment name

Each environment pool is configured with `AllocationResourceTags` that match `Environment` to `Production`, `UAT`, or `Development`, enabling automatic pool selection by the VPC template's Lambda function.

---

> See also: [Reference: Interfaces](../reference/interfaces.md) | [Architecture: Patterns](../architecture/patterns.md)
