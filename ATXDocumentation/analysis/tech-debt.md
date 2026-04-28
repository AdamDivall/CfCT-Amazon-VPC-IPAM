# Technical Debt Assessment

> Back to: [README](../README.md) | [Code Metrics](code-metrics.md) | [Complexity Analysis](complexity-analysis.md) | [Dependency Analysis](dependency-analysis.md) | [Security Patterns](security-patterns.md)

## Consolidated Technical Debt Findings

This document consolidates all technical debt findings from the comprehensive codebase analysis, organized by severity.

---

## High Severity

### TD-01: Python 3.9 Lambda Runtime Approaching EOL

**Location:** `vpc-ipam-delegation.yaml` (line ~126), `custom-vpc.yaml` (line ~120)  
**Category:** EOL/Deprecated Runtime  
**Impact:** Lambda functions will become non-deployable after AWS deprecates python3.9  
**Remediation:** Change `Runtime: python3.9` to `Runtime: python3.12` in both templates  
**Effort:** Low — no code changes needed, only configuration  
**AWS Transformation:** `AWS/python-version-upgrade` available

---

## Medium Severity

### TD-02: RAM Share References Non-Existent Resources

**Location:** `vpc-ipam-pools.yaml` → `rRamShareIpamEnvironmentPoolIpv4.ResourceArns`  
**Category:** Potential Bug / Deployment Blocker  
**Impact:** Template cannot be deployed as-is — CloudFormation will fail on unresolved `!GetAtt` references for `rIpamPoolRegional3ProdIpv4`, `rIpamPoolRegional3UatIpv4`, `rIpamPoolRegional3DevIpv4`  
**Remediation:** Remove Region 3 references or add Region 3 pool resource definitions  
**Effort:** Low

### TD-03: Duplicate Lambda Code

**Location:** `lambda/lambda-vpc-ipam-delegation.py` (34 lines) duplicates inline code in `vpc-ipam-delegation.yaml`  
**Category:** Code Quality / Maintainability  
**Impact:** Changes must be synchronized in two locations; risk of code drift  
**Remediation:** Remove standalone file or use S3-based Lambda packaging  
**Effort:** Low

### TD-04: Inconsistent pTagEnvironment AllowedValues

**Location:** `custom-vpc.yaml` allows `[Production, Development]` while other templates allow `[Production, UAT, Development]`  
**Category:** Configuration Consistency  
**Impact:** UAT environments cannot provision VPCs even though UAT IPAM pools exist  
**Remediation:** Add `UAT` to `pTagEnvironment` AllowedValues in `custom-vpc.yaml`  
**Effort:** Low

### TD-05: Incomplete Error Handling in Lambda Functions

**Location:** Both Lambda functions  
**Category:** Code Quality / Reliability  
**Impact:** If API response `Success` is `False` (not an exception), no cfnresponse is sent, causing 60s timeout. Unhandled non-ClientError exceptions crash Lambda.  
**Remediation:** Add generic `except Exception` handler and fallback cfnresponse logic  
**Effort:** Low

---

## Low Severity

### TD-06: Overly Broad IAM Permissions

**Location:** `vpc-ipam-delegation.yaml` → `rIpamLambdaRoleDelegate`  
**Category:** Security  
**Impact:** `iam:CreateServiceLinkedRole` with `Resource: "*"` is broader than necessary  
**Remediation:** Scope to IPAM service-linked role ARN  
**Effort:** Low

### TD-07: Hardcoded 2-Region Architecture

**Location:** `vpc-ipam-pools.yaml`  
**Category:** Architecture / Scalability  
**Impact:** Adding a third region requires manually duplicating 4+ resource definitions  
**Remediation:** Consider CloudFormation macros, CDK, or Terraform for dynamic region support  
**Effort:** High (architectural change)

### TD-08: No CloudWatch Logs KMS Encryption

**Location:** `vpc-ipam-delegation.yaml`, `custom-vpc.yaml`  
**Category:** Security / Compliance  
**Impact:** Lambda logs stored without customer-managed encryption  
**Remediation:** Add `KmsKeyId` property to `AWS::Logs::LogGroup` resources  
**Effort:** Low

### TD-09: No CloudFormation Outputs

**Location:** All 3 templates  
**Category:** Operations / Maintainability  
**Impact:** No programmatic access to created resource IDs; no cross-stack references  
**Remediation:** Add Outputs section to each template  
**Effort:** Low

### TD-10: No VPC Flow Logs

**Location:** `custom-vpc.yaml`  
**Category:** Security / Compliance  
**Impact:** No network traffic monitoring or audit trail  
**Remediation:** Add `AWS::EC2::FlowLog` resource  
**Effort:** Low

### TD-11: List Parameters Without Validation

**Location:** `vpc-ipam-pools.yaml` — `pOperatingRegionList`, CIDR list parameters  
**Category:** Input Validation  
**Impact:** Malformed region names or CIDRs could cause confusing deployment failures  
**Remediation:** Add CloudFormation Guard rules or Custom Resource validation  
**Effort:** Medium

---

## Debt Distribution Summary

| Severity | Count | Primary Categories |
|----------|-------|-------------------|
| **High** | 1 | EOL Runtime |
| **Medium** | 4 | Bug, Code Quality, Configuration |
| **Low** | 6 | Security, Architecture, Operations |
| **Total** | **11** | |

---

> See also: [Technical Debt Report](../technical-debt-report.md) | [Technical Debt: Remediation Plan](../technical-debt/remediation-plan.md)
