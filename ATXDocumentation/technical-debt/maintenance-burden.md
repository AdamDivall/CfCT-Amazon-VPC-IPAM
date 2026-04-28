# Maintenance Burden Analysis

> Back to: [Technical Debt Report](../technical-debt-report.md) | [Summary](summary.md) | [Outdated Components](outdated-components.md) | [Remediation Plan](remediation-plan.md)

## Overview

The CfCT Amazon VPC IPAM project has several areas that impose ongoing maintenance burden. While the project is small (~925 LOC), certain design choices increase the cost of making changes and the risk of introducing errors.

## High Maintenance Areas

### 1. Duplicate Lambda Code — **Medium Burden**

**Files Affected:**
- `lambda/lambda-vpc-ipam-delegation.py` (34 lines)
- `vpc-ipam-delegation.yaml` — `rIpamLambdaDelegate` ZipFile inline code (34 lines)

**Problem:** The Lambda handler for IPAM delegation exists in two places — as a standalone Python file and as inline code within the CloudFormation template. Any bug fix or enhancement must be applied in both locations. The standalone file is not referenced by any deployment mechanism.

**Maintenance Cost:** Every code change requires manual synchronization between two files. Risk of code drift is significant.

**Recommendation:** Eliminate one copy. Either:
1. Remove `lambda/lambda-vpc-ipam-delegation.py` (if inline ZipFile is the deployment mechanism), or
2. Package the Lambda from `lambda/` directory using S3 and remove the inline code

### 2. Hardcoded Multi-Region Resource Blocks — **Medium Burden**

**Files Affected:**
- `vpc-ipam-pools.yaml` — Regional IPAM pool resources (6 environment pool resources for 2 regions)

**Problem:** Each region requires 4 manually-defined CloudFormation resources: 1 regional pool + 3 environment pools (Prod, UAT, Dev). Adding a new region means:
1. Adding 4 new resource definitions (copy/paste with region index changes)
2. Updating the RAM share resource ARN list
3. Updating the top-level IPAM OperatingRegions
4. Updating the top-level pool ProvisionedCidrs

**Maintenance Cost:** Significant effort for region expansion. High risk of copy-paste errors (as evidenced by the existing Region 3 reference bug in the RAM share).

**Recommendation:** Consider CloudFormation macros, nested stacks with parameter-driven loops, or CDK/Terraform for dynamic region support.

### 3. Non-Existent Resource References in RAM Share — **High Burden**

**Files Affected:**
- `vpc-ipam-pools.yaml` — `rRamShareIpamEnvironmentPoolIpv4`

**Problem:** The RAM ResourceShare references three Region 3 pool resources (`rIpamPoolRegional3ProdIpv4`, `rIpamPoolRegional3UatIpv4`, `rIpamPoolRegional3DevIpv4`) that do not exist in the template. This is a deployment blocker — the template cannot be deployed as-is.

**Maintenance Cost:** Immediate fix required. This is either:
- Leftover from an incomplete 3-region expansion, or
- A forward declaration for a planned 3rd region that was never implemented

**Recommendation:** Remove the Region 3 references from the RAM share, or add the missing resources.

### 4. Inconsistent Parameter Definitions — **Low Burden**

**Files Affected:**
- `vpc-ipam-delegation.yaml` — `pTagEnvironment: [Production, UAT, Development]`
- `custom-vpc.yaml` — `pTagEnvironment: [Production, Development]` (missing UAT)

**Problem:** Templates that are meant to work together have inconsistent parameter validation, which can cause deployment failures or unexpected behavior when environments don't align.

**Maintenance Cost:** Requires careful manual review when modifying parameters across templates.

### 5. No CloudFormation Outputs — **Low Burden**

**Files Affected:** All 3 CloudFormation templates

**Problem:** None of the templates define CloudFormation Outputs. This means:
- No cross-stack references are possible
- No easy way to verify successful deployments
- No programmatic access to created resource IDs

**Maintenance Cost:** Troubleshooting and integration require manual AWS Console/CLI lookups.

## Maintenance Burden Matrix

| Area | Change Frequency | Error Risk | Impact | Overall Burden |
|------|-----------------|------------|--------|----------------|
| Duplicate Lambda code | On every Lambda change | High | Medium | **Medium** |
| Multi-region resource blocks | On region addition | High | High | **Medium** |
| RAM share references (bug) | Immediate | Critical | High | **High** |
| Parameter inconsistencies | On parameter changes | Medium | Medium | **Low** |
| No CloudFormation outputs | On troubleshooting | Low | Low | **Low** |

---

> See also: [Remediation Plan](remediation-plan.md) | [Architecture Components](../architecture/components.md)
