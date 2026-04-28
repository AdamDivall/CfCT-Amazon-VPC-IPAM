# Project Overview

> Back to: [README](README.md) | [Technical Debt Report](technical-debt-report.md)

## Purpose

The **CfCT Amazon VPC IPAM** project provides an Infrastructure-as-Code (IaC) solution for deploying and managing Amazon VPC IP Address Manager (IPAM) across a multi-account AWS environment governed by AWS Control Tower.

It solves the problem of **centralized IP address management** at scale:
- Prevents overlapping IP address spaces across accounts and regions
- Automates VPC CIDR allocation from managed pools
- Supports multiple SDLC environments (Production, UAT, Development) with dedicated IP ranges
- Integrates with AWS Control Tower for automated deployment

## Technology Stack

| Technology | Version | Role |
|-----------|---------|------|
| AWS CloudFormation | 2010-09-09 | Infrastructure definition |
| Python | 3.9 | Lambda runtime (**⚠️ approaching EOL**) |
| boto3 | Bundled with Lambda | AWS SDK for Python |
| cfnresponse | Bundled with Lambda | CloudFormation Custom Resource helper |
| CfCT | N/A | Deployment mechanism |
| AWS RAM | N/A | Cross-account resource sharing |
| Amazon VPC IPAM | N/A | IP address management |

## Architecture Summary

The solution uses a **three-template architecture** deployed to different accounts in the AWS Organization:

1. **IPAM Delegation** (`vpc-ipam-delegation.yaml`) — Deployed to the **Management Account**. Uses a Lambda-backed Custom Resource to delegate IPAM administration to the Network Account via the EC2 IPAM organization API.

2. **IPAM Pool Configuration** (`vpc-ipam-pools.yaml`) — Deployed to the **Network Account**. Creates the IPAM instance, custom scope, and a hierarchical pool structure (Top → Regional → Environment). Shares environment pools to the entire Organization via AWS RAM.

3. **Custom VPC** (`custom-vpc.yaml`) — Deployed to **member accounts**. Uses a Lambda-backed Custom Resource to look up the appropriate IPAM pool by region and environment tag, then creates a VPC with an IPAM-allocated CIDR, 9 subnets (3 tiers × 3 AZs), Internet Gateway, NAT Gateways, and routing.

## Deployment Model

```
CfCT (manifest.yaml)
  ├── Management Account → vpc-ipam-delegation.yaml (Step 1)
  ├── Network Account    → vpc-ipam-pools.yaml      (Step 2)
  └── Member Accounts    → custom-vpc.yaml           (Step 3)
```

Templates must be deployed in order. CfCT uses CloudFormation StackSets under the hood.

## Key Components

| Component | Files | Resources | Description |
|-----------|-------|-----------|-------------|
| IPAM Delegation | `vpc-ipam-delegation.yaml`, `.json` | 4 | Lambda + Custom Resource for delegated admin |
| IPAM Pools | `vpc-ipam-pools.yaml`, `.json` | 12 | IPAM, Scope, 9 Pools, RAM Share |
| Custom VPC | `custom-vpc.yaml` | 45 | Lambda, VPC, 9 Subnets, IGW, 3 NATs, Routing |
| Lambda (standalone) | `lambda/lambda-vpc-ipam-delegation.py` | — | Unused duplicate of inline Lambda |

## Codebase Statistics

- **Total files:** 7
- **Total lines:** 1,041
- **CloudFormation resources:** 61 (across 3 templates)
- **Lambda functions:** 2 (inline ZipFile)
- **Languages:** Python 3.9, CloudFormation YAML, JSON

## Critical Issues

1. **Python 3.9 EOL** — Both Lambda functions use `python3.9` runtime, which is approaching end-of-life. See [Technical Debt Report](technical-debt-report.md).
2. **RAM Share Bug** — `vpc-ipam-pools.yaml` references non-existent Region 3 pool resources. See [Maintenance Burden](technical-debt/maintenance-burden.md).
3. **Duplicate Code** — Standalone Lambda file duplicates inline CloudFormation code. See [Technical Debt Summary](technical-debt/summary.md).

## Related Documentation

- [Architecture: System Overview](architecture/system-overview.md)
- [Architecture: Components](architecture/components.md)
- [Architecture: Dependencies](architecture/dependencies.md)
- [Reference: Program Structure](reference/program-structure.md)
- [Analysis: Code Metrics](analysis/code-metrics.md)
- [Technical Debt Report](technical-debt-report.md)
- [Migration: Component Order](migration/component-order.md)
