# System Overview

> Back to: [README](../README.md) | [Components](components.md) | [Dependencies](dependencies.md) | [Patterns](patterns.md)

## Purpose

This project provides an Infrastructure-as-Code (IaC) solution for deploying and managing **Amazon VPC IP Address Manager (IPAM)** across a multi-account AWS environment governed by **AWS Control Tower**. It automates three core capabilities:

1. **IPAM Delegated Administration** — Delegates IPAM management from the Management Account to the Network Account
2. **IPAM Pool Hierarchy** — Creates a hierarchical IP address pool structure supporting multiple regions and SDLC environments
3. **VPC Provisioning** — Creates VPCs with IPAM-allocated CIDR blocks, ensuring non-overlapping IP address spaces

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Infrastructure Definition | AWS CloudFormation | 2010-09-09 |
| Compute (Custom Resources) | AWS Lambda | Python 3.9 |
| SDK | boto3 | Bundled with Lambda runtime |
| CloudFormation Helper | cfnresponse | Bundled with Lambda runtime |
| Deployment Mechanism | Customizations for Control Tower (CfCT) | N/A |
| Resource Sharing | AWS Resource Access Manager (RAM) | N/A |
| IP Management | Amazon VPC IPAM | N/A |

## Deployment Model

The solution is deployed through **Customizations for Control Tower (CfCT)**, which orchestrates CloudFormation StackSet deployments across AWS accounts and regions:

- **`vpc-ipam-delegation.yaml`** → Deployed to the **Management Account** (Control Tower home region only)
- **`vpc-ipam-pools.yaml`** → Deployed to the **Network Account** (delegated IPAM admin account)
- **`custom-vpc.yaml`** → Deployed to **member accounts** that need VPCs (any region with IPAM pools)

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Organization                          │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Management Acct  │    │  Network Acct   │                │
│  │                  │    │  (IPAM Admin)   │                │
│  │ vpc-ipam-        │───▶│ vpc-ipam-       │                │
│  │ delegation.yaml  │    │ pools.yaml      │                │
│  │                  │    │                  │                │
│  │ Lambda: Delegate │    │ IPAM + Pools    │                │
│  │ IPAM Admin       │    │ RAM Shares      │                │
│  └─────────────────┘    └────────┬────────┘                │
│                                  │ RAM Share                │
│                    ┌─────────────┼─────────────┐           │
│                    ▼             ▼              ▼           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  Member Acct │ │  Member Acct │ │  Member Acct │       │
│  │              │ │              │ │              │       │
│  │ custom-      │ │ custom-      │ │ custom-      │       │
│  │ vpc.yaml     │ │ vpc.yaml     │ │ vpc.yaml     │       │
│  │              │ │              │ │              │       │
│  │ VPC + Subnets│ │ VPC + Subnets│ │ VPC + Subnets│       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

1. **Delegated Administration Pattern:** IPAM is managed from the Network Account, not the Management Account, following AWS best practice of least privilege for the Management Account.
2. **Hierarchical Pool Design:** IPAM pools are organized in a 3-tier hierarchy (Top → Regional → Environment) enabling granular IP address management.
3. **Custom Resources for API Gaps:** Lambda-backed Custom Resources bridge CloudFormation capability gaps for IPAM delegation and pool ID discovery.
4. **Organization-Wide RAM Sharing:** IPAM pools are shared to the entire Organization, allowing any member account to provision VPCs.
5. **CfCT Deployment:** Leverages Customizations for Control Tower for automated, account-targeted deployment.

---

> See also: [Components](components.md) | [Dependencies](dependencies.md) | [Technical Debt Report](../technical-debt-report.md)
