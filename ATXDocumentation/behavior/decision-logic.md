> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Decision Logic

> Back to: [README](../README.md) | [Business Logic](business-logic.md) | [Workflows](workflows.md) | [Error Handling](error-handling.md)

## Overview

This document captures all decision points found in the application code across the Lambda functions and CloudFormation templates.

---

## Decision Point 1: CloudFormation RequestType Branching (Delegation Lambda)

**Source:** `vpc-ipam-delegation.yaml` (inline ZipFile), `lambda/lambda-vpc-ipam-delegation.py`

```python
if (event['RequestType'] == 'Create' or event['RequestType'] == 'Update'):
    # Enable IPAM delegation
elif (event['RequestType'] == 'Delete'):
    # Disable IPAM delegation
else:
    # No-op, signal SUCCESS
```

| Condition | Action |
|-----------|--------|
| `RequestType == 'Create'` | Call `enable_ipam_organization_admin_account` |
| `RequestType == 'Update'` | Call `enable_ipam_organization_admin_account` (idempotent re-enable) |
| `RequestType == 'Delete'` | Call `disable_ipam_organization_admin_account` |
| Any other value | Signal `cfnresponse.SUCCESS` (passthrough) |

**Note:** Create and Update follow the same code path. The enable API is idempotent — calling it when delegation is already active is safe.

---

## Decision Point 2: API Success Check (Delegation Lambda)

**Source:** `vpc-ipam-delegation.yaml` (inline ZipFile), `lambda/lambda-vpc-ipam-delegation.py`

```python
if response['Success'] == True:
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
```

| Condition | Action |
|-----------|--------|
| `response['Success'] == True` | Signal CloudFormation SUCCESS |
| `response['Success'] != True` | **No action** — cfnresponse is never sent ⚠️ |
| `ClientError` exception raised | Signal CloudFormation FAILED |

**⚠️ Potential Issue:** If `response['Success']` is `False` (not a `ClientError`), the function falls through without sending a cfnresponse signal. This would cause CloudFormation to wait until the Lambda timeout (60s) and then fail the Custom Resource.

---

## Decision Point 3: CloudFormation RequestType Branching (Pool Lookup Lambda)

**Source:** `custom-vpc.yaml` (inline ZipFile)

```python
if event['RequestType'] == 'Create':
    # Query IPAM pools and find matching pool
if event['RequestType'] == 'Update':
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
if event['RequestType'] == 'Delete':
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
```

| Condition | Action |
|-----------|--------|
| `RequestType == 'Create'` | Execute full pool lookup logic |
| `RequestType == 'Update'` | Signal SUCCESS immediately (no-op) |
| `RequestType == 'Delete'` | Signal SUCCESS immediately (no-op) |

**Note:** Uses `if` instead of `elif` — all three conditions are evaluated independently. For `Create`, the code falls through to also check `Update` and `Delete` (which won't match). Not a bug but indicates non-standard control flow.

---

## Decision Point 4: Empty Pool Results Check

**Source:** `custom-vpc.yaml` (inline ZipFile)

```python
if len(ipam_pool['IpamPools']) == 0:
    print(f"No IPAM Pools Configured in {region}")
```

| Condition | Action |
|-----------|--------|
| No pools returned | Print warning; status remains `FAILED` |
| Pools returned | Continue to iteration |

**Note:** After this check, the code continues to the `for` loop which simply won't execute on an empty list. The `status` variable defaults to `cfnresponse.FAILED`.

---

## Decision Point 5: Pool Allocation Tag Matching

**Source:** `custom-vpc.yaml` (inline ZipFile)

```python
for ip_pool in ipam_pool['IpamPools']:
    if ip_pool['AllocationResourceTags']:
        for tag in ip_pool['AllocationResourceTags']:
            if tag['Value'] == environment:
                # Found matching pool
                break
            else:
                print(f"No IPAM Pools with Allocation Resource Tags that match the Environment")
    elif len(ip_pool['AllocationResourceTags']) == 0:
        print(f"IPAM Pool has no Allocation Resource Tags applied")
```

| Condition | Action |
|-----------|--------|
| Pool has `AllocationResourceTags` and a tag value matches `ENVIRONMENT` | Capture Pool ID, set SUCCESS, break |
| Pool has `AllocationResourceTags` but no value matches | Print warning for each non-matching tag |
| Pool has empty `AllocationResourceTags` list | Print "no tags applied" |
| Pool has no `AllocationResourceTags` key | Truthy check passes for empty list → goes to `elif` |

**Note:** The matching logic only checks tag `Value`, not tag `Key`. It matches any tag whose value equals the environment name, regardless of the key name. This works because IPAM pool AllocationResourceTags in `vpc-ipam-pools.yaml` use `Key: Environment`.

---

## Decision Point 6: VPC Size Mapping

**Source:** `custom-vpc.yaml` → `mVpcSize` Mapping + `pVpcSize` Parameter

```yaml
pVpcSize:
  AllowedValues: ["Small", "Medium", "Large"]
```

| VPC Size | VPC Netmask | Public Subnet Bits | Hybrid Subnet Bits | Private Subnet Bits |
|----------|-------------|-------------------|--------------------|--------------------|
| Small | /22 | 4 | 6 | 6 |
| Medium | /20 | 4 | 8 | 8 |
| Large | /19 | 4 | 9 | 9 |

This decision is made at CloudFormation parameter selection time and controls the VPC and subnet sizing.

---

## Decision Point 7: Environment Selection Across Templates

**Source:** All 3 templates → `pTagEnvironment` parameter

| Template | Allowed Values | Impact |
|----------|---------------|--------|
| `vpc-ipam-delegation.yaml` | Production, UAT, Development | Tag applied to resources |
| `vpc-ipam-pools.yaml` | Production, UAT, Development | Tag applied to IPAM resources |
| `custom-vpc.yaml` | Production, Development ⚠️ | Determines which IPAM pool is selected + resource tags |

**⚠️ Inconsistency:** `custom-vpc.yaml` is missing `UAT` from the allowed values, preventing UAT VPC provisioning even though UAT pools exist.

---

> See also: [Business Logic](business-logic.md) | [Reference: Data Models](../reference/data-models.md)
