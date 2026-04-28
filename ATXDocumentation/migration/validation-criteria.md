# Validation Criteria

> Back to: [README](../README.md) | [Component Order](component-order.md) | [Test Specifications](test-specifications.md)

## Overview

Success criteria for validating a successful deployment or migration of the CfCT Amazon VPC IPAM solution.

---

## VC-01: IPAM Delegation Validation

### Criteria

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | CloudFormation stack status is `CREATE_COMPLETE` | AWS Console → CloudFormation → Stack status |
| 2 | Lambda function created with correct runtime | `aws lambda get-function --function-name lambda-vpc-ipam-delegate-admin` |
| 3 | IAM role created with correct policies | AWS Console → IAM → Role → Permissions |
| 4 | CloudWatch Log Group created with configured retention | `aws logs describe-log-groups --log-group-name-prefix /aws/lambda/lambda-vpc-ipam-delegate-admin` |
| 5 | Network Account is IPAM delegated administrator | `aws organizations list-delegated-administrators --service-principal ipam.amazonaws.com` |
| 6 | Custom Resource (rIpam) status is `CREATE_COMPLETE` | CloudFormation stack resources tab |

### Success Definition
All 6 criteria must pass. If criterion 5 fails, the delegation Lambda encountered an error.

---

## VC-02: IPAM Pool Configuration Validation

### Criteria

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | CloudFormation stack status is `CREATE_COMPLETE` | AWS Console → CloudFormation → Stack status |
| 2 | IPAM instance created with correct operating regions | `aws ec2 describe-ipams` |
| 3 | Custom IPAM scope created (type: private) | `aws ec2 describe-ipam-scopes --filters Name=ipam-scope-type,Values=private` |
| 4 | Top-level pool provisioned with 3 CIDRs | `aws ec2 describe-ipam-pools` → filter by description "Top Level Pool" |
| 5 | 2 Regional pools created (one per operating region) | `aws ec2 describe-ipam-pools` → filter by source pool ID |
| 6 | 6 Environment pools created (3 envs × 2 regions) | `aws ec2 describe-ipam-pools` → filter by AllocationResourceTags |
| 7 | Each environment pool has correct Locale | Verify Locale matches the expected operating region |
| 8 | Each environment pool has correct AllocationResourceTags | Verify `Environment` tag with correct value (Production/UAT/Development) |
| 9 | RAM share created with all environment pool ARNs | `aws ram get-resource-shares --resource-owner SELF` |
| 10 | RAM share has `AllowExternalPrincipals: false` | Verify in RAM share details |
| 11 | RAM share principal is the Organization ARN | Verify principal matches `arn:aws:organizations::<MgmtAcct>:organization/<OrgId>` |

### Success Definition
All 11 criteria must pass. Criterion 9 will fail if Region 3 references are not fixed.

---

## VC-03: Custom VPC Validation

### Criteria

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | CloudFormation stack status is `CREATE_COMPLETE` | AWS Console → CloudFormation → Stack status |
| 2 | Pool Lookup Lambda created with correct runtime and environment | `aws lambda get-function` → check Runtime and Environment |
| 3 | Custom Resource returned a valid IPAM Pool ID | CloudFormation events → `rCustomGetPoolId` → ResponseData |
| 4 | VPC created with IPAM-allocated CIDR | `aws ec2 describe-vpcs` → verify CIDR from IPAM pool range |
| 5 | VPC CIDR netmask matches selected VPC size | Small=/22, Medium=/20, Large=/19 |
| 6 | 3 Public subnets created (one per AZ) | `aws ec2 describe-subnets --filters Name=vpc-id,Values=<VpcId>` |
| 7 | 3 Hybrid subnets created (one per AZ) | Same as above, filter by CIDR range |
| 8 | 3 Private subnets created (one per AZ) | Same as above, filter by CIDR range |
| 9 | Internet Gateway attached to VPC | `aws ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values=<VpcId>` |
| 10 | 3 NAT Gateways created (one per AZ) | `aws ec2 describe-nat-gateways --filter Name=vpc-id,Values=<VpcId>` |
| 11 | 3 Elastic IPs allocated | `aws ec2 describe-addresses` → associated with NAT Gateways |
| 12 | Public route table has default route to IGW | `aws ec2 describe-route-tables` → 0.0.0.0/0 → IGW |
| 13 | Hybrid route tables have default route to NAT | Per-AZ route tables with 0.0.0.0/0 → NAT-GW |
| 14 | Private route tables have default route to NAT | Per-AZ route tables with 0.0.0.0/0 → NAT-GW |
| 15 | All subnets associated with correct route tables | Verify subnet-route table associations |
| 16 | All resources tagged with Environment key | Verify tags on VPC, subnets, NAT Gateways, EIPs |

### Success Definition
All 16 criteria must pass.

---

## VC-04: Cross-Component Validation

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| 1 | VPC CIDR falls within IPAM pool's provisioned range | Compare VPC CIDR with pool CIDR |
| 2 | IPAM allocation record exists for the VPC | `aws ec2 get-ipam-pool-allocations --ipam-pool-id <PoolId>` |
| 3 | Multiple VPCs from same pool don't overlap | Deploy two VPC stacks and verify non-overlapping CIDRs |
| 4 | VPCs in different environments use different pools | Deploy with `Production` and `Development` tags; verify different pool IDs |

---

## VC-05: Remediation Validation

After applying technical debt fixes:

| # | Fix | Validation |
|---|-----|-----------|
| 1 | Python 3.12 runtime | Lambda function reports `python3.12` runtime |
| 2 | RAM share Region 3 fix | Template validates with `aws cloudformation validate-template` |
| 3 | pTagEnvironment alignment | `custom-vpc.yaml` accepts `UAT` as environment parameter |
| 4 | Duplicate Lambda removal | Only one copy of delegation Lambda code exists |

---

> See also: [Technical Debt: Remediation Plan](../technical-debt/remediation-plan.md) | [Test Specifications](test-specifications.md)
