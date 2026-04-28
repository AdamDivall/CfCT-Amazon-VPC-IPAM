# Technical Debt Summary

> Back to: [Technical Debt Report](../technical-debt-report.md) | [Outdated Components](outdated-components.md) | [Maintenance Burden](maintenance-burden.md) | [Remediation Plan](remediation-plan.md)

## Overview

The CfCT Amazon VPC IPAM project carries a moderate level of technical debt, concentrated primarily around runtime currency and code maintainability. The project is a small IaC solution (~925 LOC across 7 files) designed for multi-account VPC IPAM management via AWS Control Tower.

## Debt Categories

### 1. Runtime & Framework Currency — **High**

| Item | Current | Recommended | Severity |
|------|---------|-------------|----------|
| Python Lambda Runtime | 3.9 | 3.12+ | **High** |
| boto3 (bundled with Lambda) | Unpinned | Pin or use Lambda layer | **Low** |

Python 3.9 reaches end-of-life in October 2025. AWS will deprecate the `python3.9` Lambda runtime, preventing new function creation and eventually blocking updates to existing functions. This is the highest priority technical debt item.

### 2. Code Quality — **Medium**

| Item | Description | Severity |
|------|-------------|----------|
| Duplicate Lambda code | Standalone file mirrors inline CloudFormation code | **Medium** |
| Non-existent resource references | RAM share references Region 3 pools that don't exist | **Medium** |
| Inconsistent parameter validation | `pTagEnvironment` AllowedValues differ between templates | **Medium** |
| Unused standalone Lambda file | `lambda/lambda-vpc-ipam-delegation.py` not referenced by any template | **Medium** |

### 3. Security & Compliance — **Low**

| Item | Description | Severity |
|------|-------------|----------|
| Wildcard IAM resources | `Resource: "*"` on all IAM policies | **Low** |
| No KMS encryption | CloudWatch Logs and Lambda env vars unencrypted | **Low** |
| No VPC Flow Logs | custom-vpc.yaml creates a VPC but no flow logs resource | **Low** |

### 4. Architecture & Scalability — **Low**

| Item | Description | Severity |
|------|-------------|----------|
| Hardcoded region count | Template supports exactly 2 regions | **Low** |
| No shared parameter validation | 3 templates with independent parameter definitions | **Low** |
| No CloudFormation outputs | Templates don't export values for cross-stack references | **Low** |

## Severity Distribution

- **High:** 1 item (Python 3.9 EOL)
- **Medium:** 4 items (code duplication, resource reference bug, parameter inconsistency, unused file)
- **Low:** 6 items (IAM permissions, encryption, flow logs, region limits, parameter validation, outputs)

## Recommended Priority Order

1. Fix the non-existent Region 3 resource references (deployment blocker)
2. Upgrade Python 3.9 to 3.12+ (EOL deadline)
3. Align `pTagEnvironment` across all templates
4. Remove or consolidate duplicate Lambda code
5. Address security hardening items
6. Consider architectural improvements for scalability

---

> See also: [Analysis Tech Debt](../analysis/tech-debt.md) | [Remediation Plan](remediation-plan.md)
