# Remediation Plan

> Back to: [Technical Debt Report](../technical-debt-report.md) | [Summary](summary.md) | [Outdated Components](outdated-components.md) | [Maintenance Burden](maintenance-burden.md)

## Prioritized Remediation Actions

Actions are ordered by severity and deployment impact. Items marked as deployment blockers should be addressed first.

---

### Action 1: Fix RAM Share Non-Existent Resource References — **High Priority**

**Severity:** Medium (classified as a deployment blocker)  
**Effort:** Low  
**Files:** `vpc-ipam-pools.yaml`

**Current Issue:**
```yaml
# These resources do NOT exist in the template:
- !GetAtt rIpamPoolRegional3ProdIpv4.Arn
- !GetAtt rIpamPoolRegional3UatIpv4.Arn
- !GetAtt rIpamPoolRegional3DevIpv4.Arn
```

**Remediation Options:**
- **Option A (Remove):** Delete the three Region 3 references from `rRamShareIpamEnvironmentPoolIpv4.Properties.ResourceArns`
- **Option B (Add):** Create `rIpamPoolRegional3Ipv4`, `rIpamPoolRegional3ProdIpv4`, `rIpamPoolRegional3UatIpv4`, and `rIpamPoolRegional3DevIpv4` resources following the same pattern as Region 1 and Region 2

**Verification:** Template passes `aws cloudformation validate-template` without errors.

---

### Action 2: Upgrade Python Runtime to 3.12+ — **High Priority**

**Severity:** High  
**Effort:** Low  
**Files:** `vpc-ipam-delegation.yaml`, `custom-vpc.yaml`

**Current State:** `Runtime: python3.9`  
**Target State:** `Runtime: python3.12`

**Steps:**
1. Change `Runtime: python3.9` to `Runtime: python3.12` in `vpc-ipam-delegation.yaml` (line ~126)
2. Change `Runtime: python3.9` to `Runtime: python3.12` in `custom-vpc.yaml` (line ~120)
3. Test Lambda function execution in a non-production environment
4. Verify `boto3`, `cfnresponse`, and `botocore` imports work correctly

**Risk Assessment:** Low risk. No Python 3.9-specific syntax or features are used. All imports are AWS Lambda bundled libraries.

**AWS Transformation Available:** `AWS/python-version-upgrade` can automate this change.

---

### Action 3: Align pTagEnvironment Across Templates — **Medium Priority**

**Severity:** Medium  
**Effort:** Low  
**Files:** `custom-vpc.yaml`

**Current State:**
```yaml
# custom-vpc.yaml
AllowedValues:
  - "Production"
  - "Development"
```

**Target State:**
```yaml
AllowedValues:
  - "Production"
  - "UAT"
  - "Development"
```

**Verification:** All templates accept the same set of environment values.

---

### Action 4: Consolidate Duplicate Lambda Code — **Medium Priority**

**Severity:** Medium  
**Effort:** Low  
**Files:** `lambda/lambda-vpc-ipam-delegation.py`, `vpc-ipam-delegation.yaml`

**Options:**
- **Option A (Remove standalone):** Delete `lambda/lambda-vpc-ipam-delegation.py` since it's not referenced by any deployment mechanism. Keep inline ZipFile code.
- **Option B (Use S3 packaging):** Upload `lambda/lambda-vpc-ipam-delegation.py` to S3 and change the CloudFormation template to use `Code.S3Bucket`/`Code.S3Key` instead of `ZipFile`. Remove the inline code.

**Recommendation:** Option A is simplest. Option B is better for testability and larger Lambda functions.

---

### Action 5: Tighten IAM Permissions — **Low Priority**

**Severity:** Low  
**Effort:** Medium  
**Files:** `vpc-ipam-delegation.yaml`, `custom-vpc.yaml`

**Current State:** Both IAM roles use `Resource: "*"` for all actions.

**Target State:** Restrict `iam:CreateServiceLinkedRole` to the specific service-linked role ARN:
```yaml
Resource: "arn:aws:iam::*:role/aws-service-role/ipam.amazonaws.com/*"
```

Note: EC2 IPAM and Organizations API calls generally do not support resource-level permissions, so `"*"` is acceptable for those actions.

---

### Action 6: Add CloudWatch Logs KMS Encryption — **Low Priority**

**Severity:** Low  
**Effort:** Low  
**Files:** `vpc-ipam-delegation.yaml`, `custom-vpc.yaml`

**Steps:**
1. Create or reference a KMS key
2. Add `KmsKeyId` property to `AWS::Logs::LogGroup` resources

---

### Action 7: Add CloudFormation Outputs — **Low Priority**

**Severity:** Low  
**Effort:** Low  
**Files:** All 3 CloudFormation templates

**Recommended Outputs:**
- `vpc-ipam-delegation.yaml`: Lambda function ARN, execution role ARN
- `vpc-ipam-pools.yaml`: IPAM ID, Scope ID, Pool IDs, RAM share ARN
- `custom-vpc.yaml`: VPC ID, Subnet IDs, NAT Gateway IDs, Route Table IDs

---

## Remediation Timeline Summary

| Priority | Action | Severity | Effort |
|----------|--------|----------|--------|
| 1 | Fix RAM share references | Medium | Low |
| 2 | Upgrade Python to 3.12+ | High | Low |
| 3 | Align pTagEnvironment | Medium | Low |
| 4 | Consolidate duplicate Lambda | Medium | Low |
| 5 | Tighten IAM permissions | Low | Medium |
| 6 | Add KMS encryption | Low | Low |
| 7 | Add CloudFormation outputs | Low | Low |

---

> See also: [Architecture Patterns](../architecture/patterns.md) | [Security Patterns](../analysis/security-patterns.md)
