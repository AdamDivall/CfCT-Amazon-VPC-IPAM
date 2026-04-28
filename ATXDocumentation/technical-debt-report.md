# Technical Debt Report — CfCT Amazon VPC IPAM

## 🎯 AWS Transformation Recommendation

### **RECOMMENDED TRANSFORMATIONS: AWS/python-version-upgrade**

This codebase uses Python 3.9 as the Lambda runtime across all three CloudFormation templates. Python 3.9 is approaching end-of-life (October 2025) and should be upgraded to Python 3.12 or later. The `AWS/python-version-upgrade` transformation can automate the migration of the Python Lambda functions (both standalone and inline) to a modern, supported Python runtime.

---

## Executive Summary

This Infrastructure-as-Code (IaC) project provides AWS VPC IPAM (IP Address Manager) setup and delegation using CloudFormation and Lambda, designed for deployment via Customizations for Control Tower (CfCT). The project consists of 3 CloudFormation templates, 1 standalone Python Lambda file, and 2 JSON parameter files totaling ~925 lines of code.

The technical debt analysis reveals **1 High-severity issue** (EOL runtime), **3 Medium-severity issues** (code duplication, potential resource reference bug, and incomplete parameter validation), and **3 Low-severity issues** (overly broad IAM permissions, hardcoded region limits, and missing encryption configuration).

## Prioritized Findings Summary

| # | Finding | Severity | Category |
|---|---------|----------|----------|
| 1 | Python 3.9 Lambda runtime approaching EOL | **High** | EOL/Deprecated Runtime |
| 2 | RAM ResourceShare references non-existent Region 3 resources | **Medium** | Potential Bug |
| 3 | Duplicate Lambda code (standalone file vs inline CloudFormation) | **Medium** | Code Quality |
| 4 | Inconsistent `pTagEnvironment` AllowedValues across templates | **Medium** | Configuration Consistency |
| 5 | Overly broad IAM `Resource: "*"` permissions | **Low** | Security |
| 6 | Hardcoded 2-region support with manual expansion needed | **Low** | Architecture |
| 7 | No CloudWatch Logs encryption or Lambda environment encryption | **Low** | Security |

---

## Detailed Findings

### 1. 🔴 Python 3.9 Runtime — EOL (High)

**Location:** `vpc-ipam-delegation.yaml` (line ~126), `custom-vpc.yaml` (line ~120)

Both Lambda functions use `Runtime: python3.9`. Python 3.9 reaches end-of-life in October 2025, after which AWS Lambda will stop supporting it for new function creation and eventually for updates.

**Impact:** Functions will become non-deployable after AWS deprecates the runtime. Security patches will no longer be applied.

**Recommendation:** Upgrade to `python3.12` or `python3.13`. The code uses only `boto3`, `cfnresponse`, and standard library modules — no compatibility issues are expected.

### 2. 🟡 RAM Share References Non-Existent Resources (Medium)

**Location:** `vpc-ipam-pools.yaml`, `rRamShareIpamEnvironmentPoolIpv4` resource

The RAM ResourceShare includes ARN references to `rIpamPoolRegional3ProdIpv4`, `rIpamPoolRegional3UatIpv4`, and `rIpamPoolRegional3DevIpv4` — but these resources are **not defined** anywhere in the template. Only Region 1 and Region 2 pool resources exist.

**Impact:** CloudFormation deployment will fail with an unresolved reference error if this template is deployed as-is.

**Recommendation:** Either remove the Region 3 references from the RAM share, or add the corresponding Region 3 IPAM pool resource definitions.

### 3. 🟡 Duplicate Lambda Code (Medium)

**Location:** `lambda/lambda-vpc-ipam-delegation.py` and `vpc-ipam-delegation.yaml` (ZipFile inline code)

The standalone Python file `lambda/lambda-vpc-ipam-delegation.py` is an exact duplicate of the inline Lambda code in the CloudFormation template. The standalone file is not referenced by any template (the template uses `ZipFile` inline code).

**Impact:** Maintenance burden — changes must be synchronized in two locations. Risk of code drift.

**Recommendation:** Remove the standalone file or restructure to use S3-based Lambda code packaging instead of `ZipFile` inline code.

### 4. 🟡 Inconsistent pTagEnvironment AllowedValues (Medium)

**Location:** `vpc-ipam-delegation.yaml` vs `custom-vpc.yaml`

- `vpc-ipam-delegation.yaml` allows: `Production`, `UAT`, `Development`
- `custom-vpc.yaml` allows: `Production`, `Development` (missing `UAT`)

**Impact:** UAT environments cannot use the VPC template, even though the IPAM pools template supports UAT pool provisioning.

**Recommendation:** Align `pTagEnvironment` AllowedValues across all templates to include `Production`, `UAT`, and `Development`.

### 5. 🟢 Overly Broad IAM Permissions (Low)

**Location:** `vpc-ipam-delegation.yaml` and `custom-vpc.yaml` — IAM Role policies

Both Lambda execution roles use `Resource: "*"` for their respective EC2/Organizations permissions. While some EC2 IPAM API calls do not support resource-level permissions, the `iam:CreateServiceLinkedRole` action in the delegation template should be scoped.

**Recommendation:** Review AWS documentation for resource-level permission support and restrict where possible.

### 6. 🟢 Hardcoded 2-Region Architecture (Low)

**Location:** `vpc-ipam-pools.yaml`

The template supports exactly 2 AWS Regions with hardcoded `!Select [0, ...]` and `!Select [1, ...]` references. Adding a third region requires manually duplicating resource blocks.

**Recommendation:** Consider using CloudFormation StackSets with per-region deployments or CloudFormation macros for dynamic region support.

### 7. 🟢 No Encryption Configuration (Low)

**Location:** `vpc-ipam-delegation.yaml` and `custom-vpc.yaml`

CloudWatch Log Groups are created without KMS encryption. Lambda environment variables are not encrypted with a customer-managed KMS key.

**Recommendation:** Add KMS encryption for CloudWatch Log Groups and Lambda environment variables for defense-in-depth.

---

## Navigation

- **Detailed Technical Debt Analysis:** [technical-debt/summary.md](technical-debt/summary.md)
- **Outdated Components:** [technical-debt/outdated-components.md](technical-debt/outdated-components.md)
- **Maintenance Burden:** [technical-debt/maintenance-burden.md](technical-debt/maintenance-burden.md)
- **Remediation Plan:** [technical-debt/remediation-plan.md](technical-debt/remediation-plan.md)
- **Architecture Overview:** [architecture/system-overview.md](architecture/system-overview.md)
- **Analysis Tech Debt:** [analysis/tech-debt.md](analysis/tech-debt.md)
