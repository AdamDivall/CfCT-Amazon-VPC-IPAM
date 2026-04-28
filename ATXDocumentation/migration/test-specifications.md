# Test Specifications

> Back to: [README](../README.md) | [Component Order](component-order.md) | [Validation Criteria](validation-criteria.md)

## Overview

Test specifications for validating the deployment and functionality of each CloudFormation template and Lambda function.

---

## TC-01: CloudFormation Template Validation

### TC-01.1: Validate vpc-ipam-delegation.yaml

| Field | Value |
|-------|-------|
| **Test ID** | TC-01.1 |
| **Description** | Verify template syntax and structure |
| **Method** | `aws cloudformation validate-template --template-body file://vpc-ipam-delegation.yaml` |
| **Expected Result** | Template validates successfully; returns list of 3 parameters |
| **Prerequisites** | AWS CLI configured |

### TC-01.2: Validate vpc-ipam-pools.yaml

| Field | Value |
|-------|-------|
| **Test ID** | TC-01.2 |
| **Description** | Verify template syntax and structure |
| **Method** | `aws cloudformation validate-template --template-body file://vpc-ipam-pools.yaml` |
| **Expected Result** | ⚠️ Template will fail validation due to Region 3 `!GetAtt` references to non-existent resources. Fix required before deployment. |
| **Prerequisites** | AWS CLI configured |

### TC-01.3: Validate custom-vpc.yaml

| Field | Value |
|-------|-------|
| **Test ID** | TC-01.3 |
| **Description** | Verify template syntax and structure |
| **Method** | `aws cloudformation validate-template --template-body file://custom-vpc.yaml` |
| **Expected Result** | Template validates successfully; returns list of 3 parameters |
| **Prerequisites** | AWS CLI configured |

---

## TC-02: IPAM Delegation Lambda Behavior

### TC-02.1: Create Event — Enable Delegation

| Field | Value |
|-------|-------|
| **Test ID** | TC-02.1 |
| **Description** | Verify Lambda enables IPAM delegation on Create |
| **Input Event** | `{"RequestType": "Create", "ResourceProperties": {"accountid": "<NetworkAccountId>"}}` |
| **Expected Behavior** | Calls `enable_ipam_organization_admin_account`, receives `Success: true`, sends `cfnresponse.SUCCESS` |
| **Verification** | Network Account appears as IPAM delegated admin in Organizations |

### TC-02.2: Delete Event — Disable Delegation

| Field | Value |
|-------|-------|
| **Test ID** | TC-02.2 |
| **Description** | Verify Lambda disables IPAM delegation on Delete |
| **Input Event** | `{"RequestType": "Delete", "ResourceProperties": {"accountid": "<NetworkAccountId>"}}` |
| **Expected Behavior** | Calls `disable_ipam_organization_admin_account`, receives `Success: true`, sends `cfnresponse.SUCCESS` |
| **Verification** | Network Account is no longer IPAM delegated admin |

### TC-02.3: Error Handling — Invalid Account ID

| Field | Value |
|-------|-------|
| **Test ID** | TC-02.3 |
| **Description** | Verify Lambda handles invalid account ID gracefully |
| **Input Event** | `{"RequestType": "Create", "ResourceProperties": {"accountid": "000000000000"}}` |
| **Expected Behavior** | `ClientError` exception caught, error message printed, `cfnresponse.FAILED` sent |

---

## TC-03: Pool Lookup Lambda Behavior

### TC-03.1: Create Event — Matching Pool Found

| Field | Value |
|-------|-------|
| **Test ID** | TC-03.1 |
| **Description** | Verify Lambda finds the correct IPAM pool matching region and environment |
| **Prerequisites** | IPAM pools created with correct locale and AllocationResourceTags |
| **Environment Variables** | `ENVIRONMENT=Production`, `AWS_REGION=<matching region>` |
| **Expected Behavior** | Returns matching pool ID in `responseData['Data']`, sends `cfnresponse.SUCCESS` |

### TC-03.2: Create Event — No Matching Pool

| Field | Value |
|-------|-------|
| **Test ID** | TC-03.2 |
| **Description** | Verify Lambda handles missing pool gracefully |
| **Prerequisites** | No IPAM pools in the Lambda's region |
| **Expected Behavior** | Prints "No IPAM Pools Configured in {region}", sends `cfnresponse.FAILED` |

### TC-03.3: Update/Delete Events — No-Op

| Field | Value |
|-------|-------|
| **Test ID** | TC-03.3 |
| **Description** | Verify Lambda sends SUCCESS immediately for Update and Delete |
| **Input Event** | `{"RequestType": "Update"}` or `{"RequestType": "Delete"}` |
| **Expected Behavior** | Sends `cfnresponse.SUCCESS` with empty response data |

---

## TC-04: Stack Deployment Tests

### TC-04.1: Full Delegation Stack Deployment

| Field | Value |
|-------|-------|
| **Test ID** | TC-04.1 |
| **Description** | Deploy delegation stack to Management Account |
| **Parameters** | Valid 12-digit Network Account ID, valid environment |
| **Expected Result** | Stack reaches `CREATE_COMPLETE` status |
| **Verification** | IPAM delegated admin visible in AWS Organizations console |

### TC-04.2: Full Pools Stack Deployment

| Field | Value |
|-------|-------|
| **Test ID** | TC-04.2 |
| **Description** | Deploy pools stack to Network Account (after TC-04.1) |
| **Parameters** | Valid Org ID, Management Account ID, 2 regions, CIDRs |
| **Expected Result** | Stack reaches `CREATE_COMPLETE` (after fixing Region 3 reference bug) |
| **Verification** | IPAM, Scope, 9 Pools, and RAM Share visible in VPC IPAM console |

### TC-04.3: Full VPC Stack Deployment

| Field | Value |
|-------|-------|
| **Test ID** | TC-04.3 |
| **Description** | Deploy VPC stack to a Member Account (after TC-04.2) |
| **Parameters** | Valid environment, VPC size |
| **Expected Result** | Stack reaches `CREATE_COMPLETE` |
| **Verification** | VPC created with IPAM-allocated CIDR; 9 subnets, 3 NAT Gateways, routing configured |

---

## TC-05: Parameter Validation Tests

### TC-05.1: Invalid Account ID Format

| Field | Value |
|-------|-------|
| **Test ID** | TC-05.1 |
| **Description** | Attempt deployment with non-12-digit account ID |
| **Expected Result** | CloudFormation rejects with `ConstraintDescription` error |

### TC-05.2: Invalid Organization ID Format

| Field | Value |
|-------|-------|
| **Test ID** | TC-05.2 |
| **Description** | Attempt deployment with malformed Organization ID |
| **Expected Result** | CloudFormation rejects with `ConstraintDescription` error |

### TC-05.3: Invalid VPC Size

| Field | Value |
|-------|-------|
| **Test ID** | TC-05.3 |
| **Description** | Attempt deployment with VPC size not in AllowedValues |
| **Expected Result** | CloudFormation rejects with validation error |

---

> See also: [Validation Criteria](validation-criteria.md) | [Behavior: Error Handling](../behavior/error-handling.md)
