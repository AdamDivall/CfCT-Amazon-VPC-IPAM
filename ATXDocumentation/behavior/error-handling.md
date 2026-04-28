> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Error Handling

> Back to: [README](../README.md) | [Business Logic](business-logic.md) | [Workflows](workflows.md) | [Decision Logic](decision-logic.md)

## Overview

Error handling in this project is concentrated in the two Lambda functions. CloudFormation templates rely on standard CloudFormation error handling (rollback on resource creation failure).

---

## 1. IPAM Delegation Lambda Error Handling

**Source:** `vpc-ipam-delegation.yaml` (inline), `lambda/lambda-vpc-ipam-delegation.py`

### ClientError Exception Handling

```python
try:
    response = ec2_client.enable_ipam_organization_admin_account(...)
    if response['Success'] == True:
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
except ClientError as e:
    print(e.response['Error']['Message'])
    cfnresponse.send(event, context, cfnresponse.FAILED, e.response)
```

| Scenario | Handling |
|----------|----------|
| API call succeeds with `Success == True` | `cfnresponse.SUCCESS` → CloudFormation continues |
| API call raises `ClientError` | Print error message, `cfnresponse.FAILED` → CloudFormation rollback |
| API call succeeds with `Success == False` | ⚠️ **No cfnresponse sent** — Lambda times out after 60s, CloudFormation fails |
| Unexpected exception (not `ClientError`) | ⚠️ **Unhandled** — Lambda crashes, CloudFormation fails on timeout |

### Gap Analysis

1. **Missing fallthrough handling:** If `response['Success']` is `False`, no response is sent to CloudFormation. This causes a 60-second wait followed by a Custom Resource failure.
2. **No generic exception handler:** Only `ClientError` is caught. Other exceptions (e.g., `KeyError`, `ConnectionError`) will cause an unhandled Lambda crash.
3. **Error response data:** When `cfnresponse.FAILED` is sent, the entire `e.response` dict is sent as response data. This may contain sensitive information.

---

## 2. IPAM Pool Lookup Lambda Error Handling

**Source:** `custom-vpc.yaml` (inline ZipFile)

### ClientError Exception Handling

```python
try:
    ipam_pool = ec2_client.describe_ipam_pools(...)
    # ... pool matching logic ...
    cfnresponse.send(event, context, status, responseData)
except ClientError as e:
    print(e.response['Error']['Message'])
    cfnresponse.send(event, context, cfnresponse.FAILED, e.response)
```

| Scenario | Handling |
|----------|----------|
| API call succeeds, matching pool found | `cfnresponse.SUCCESS` with Pool ID |
| API call succeeds, no matching pool | `cfnresponse.FAILED` (status defaults to FAILED) |
| API call succeeds, no pools in region | Print warning, `cfnresponse.FAILED` |
| API call raises `ClientError` | Print error, `cfnresponse.FAILED` |
| Unexpected exception | ⚠️ **Unhandled** — Lambda crashes |

### Status Default Pattern

```python
status = cfnresponse.FAILED  # Default: assume failure
# ... search for matching pool ...
if tag['Value'] == environment:
    status = cfnresponse.SUCCESS  # Only set on match
    break
cfnresponse.send(event, context, status, responseData)
```

This is a safe default pattern — the function reports failure unless a matching pool is explicitly found.

### Gap Analysis

1. **No generic exception handler:** Same as delegation Lambda — only `ClientError` is caught.
2. **No timeout handling:** If the IPAM API is slow, the Lambda may time out (60s) without sending a cfnresponse.
3. **Partial match warning:** The `else` branch in the tag-matching loop prints a warning for every non-matching tag, which could be noisy in environments with many tags.
4. **Break scope:** The `break` statement only exits the inner `for tag` loop, not the outer `for ip_pool` loop. If a matching tag is found in an earlier pool, subsequent pools are still iterated.

---

## 3. CloudFormation-Level Error Handling

### Custom Resource Timeout

Both Lambda functions have a 60-second timeout. If the Lambda fails to send a `cfnresponse`, CloudFormation will wait up to 1 hour (default Custom Resource timeout) before marking the resource as failed.

**Recommendation:** Add a CloudFormation `Timeout` property or implement a Lambda-level catch-all handler.

### Stack Rollback Behavior

| Event | CloudFormation Behavior |
|-------|------------------------|
| Custom Resource `Create` fails | Stack rolls back, triggers `Delete` on the Custom Resource |
| Custom Resource `Delete` fails | Stack enters `DELETE_FAILED` state, requires manual intervention |
| Any resource creation fails | Full stack rollback |

### Parameter Validation

CloudFormation provides first-line validation before Lambda functions are invoked:

| Parameter | Validation | Template |
|-----------|-----------|----------|
| `pNetworkAccountId` | `AllowedPattern: ^[0-9]{12}$` | delegation |
| `pOrganizationId` | `AllowedPattern: ^[o][\-][a-z0-9]{10}$` | pools |
| `pManagementAccountId` | `AllowedPattern: ^[0-9]{12}$` | pools |
| `pVpcSize` | `AllowedValues: [Small, Medium, Large]` | custom-vpc |
| `pTagEnvironment` | `AllowedValues: [...]` | All templates |
| `pLambdaLogGroupRetention` | `AllowedValues: [1, 3, 5, ...]` | delegation, custom-vpc |

---

## Recommendations

1. Add a generic `except Exception` handler around all Lambda logic to ensure `cfnresponse` is always sent
2. Add a fallback `cfnresponse.FAILED` after the `if response['Success']` check in the delegation Lambda
3. Consider adding a Lambda `Timeout` signal handler to send `cfnresponse.FAILED` before Lambda termination
4. Avoid sending raw `e.response` as cfnresponse data — sanitize or summarize the error message

---

> See also: [Analysis: Security Patterns](../analysis/security-patterns.md) | [Technical Debt: Summary](../technical-debt/summary.md)
