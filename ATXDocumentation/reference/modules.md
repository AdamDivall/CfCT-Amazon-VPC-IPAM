# Modules

> Back to: [README](../README.md) | [Program Structure](program-structure.md) | [Interfaces](interfaces.md) | [Data Models](data-models.md) | [API Reference](api-reference.md)

## Module Organization

The project is organized into three logical modules aligned with the deployment model:

### Module 1: IPAM Delegation

**Purpose:** Enable IPAM delegated administration from Management Account to Network Account

| File | Role | Deployed To |
|------|------|-------------|
| `vpc-ipam-delegation.yaml` | CloudFormation template | Management Account |
| `vpc-ipam-delegation.json` | CfCT parameter file | — |
| `lambda/lambda-vpc-ipam-delegation.py` | Standalone Lambda source (unused duplicate) | — |

**Internal Dependencies:** None (first in deployment order)  
**External Dependencies:** `boto3`, `cfnresponse`, EC2 IPAM APIs, Organizations APIs, IAM

### Module 2: IPAM Pool Configuration

**Purpose:** Create IPAM instance, scope, hierarchical pools, and RAM sharing

| File | Role | Deployed To |
|------|------|-------------|
| `vpc-ipam-pools.yaml` | CloudFormation template | Network Account |
| `vpc-ipam-pools.json` | CfCT parameter file | — |

**Internal Dependencies:** Module 1 (delegation must be active)  
**External Dependencies:** EC2 IPAM resources, RAM, Organizations

### Module 3: Custom VPC

**Purpose:** Provision VPCs with IPAM-allocated CIDRs and full networking stack

| File | Role | Deployed To |
|------|------|-------------|
| `custom-vpc.yaml` | CloudFormation template | Member Accounts |

**Internal Dependencies:** Module 2 (IPAM pools must exist and be shared)  
**External Dependencies:** `boto3`, `cfnresponse`, EC2 IPAM APIs, VPC/Subnet/Routing resources

**Note:** No parameter JSON file exists for `custom-vpc.yaml` — parameters are expected to be managed per-account through CfCT or directly.

## Module Dependency Graph

```
Module 1: IPAM Delegation
    │
    │ Enables delegated admin
    ▼
Module 2: IPAM Pool Configuration
    │
    │ Creates pools + RAM shares
    ▼
Module 3: Custom VPC
```

## Cross-Module Data Flow

| Source Module | Target Module | Data | Mechanism |
|--------------|---------------|------|-----------|
| Module 1 | Module 2 | IPAM admin delegation | AWS Organizations delegation (not CloudFormation) |
| Module 2 | Module 3 | IPAM Pool IDs | RAM sharing + `describe_ipam_pools` API query |
| Module 2 | Module 3 | Pool allocation tags | `AllocationResourceTags` on IPAM pools |

## Shared Conventions

All modules follow these conventions:
- **Naming:** CloudFormation parameters prefixed with `p`, resources prefixed with `r`
- **Tagging:** All resources tagged with `Environment` key
- **Lambda Runtime:** Python 3.9 (both Lambda functions)
- **Lambda Memory:** 128 MB (both Lambda functions)
- **Lambda Timeout:** 60 seconds (both Lambda functions)
- **Log Retention:** Configurable via `pLambdaLogGroupRetention` parameter

---

> See also: [Architecture: Dependencies](../architecture/dependencies.md) | [Migration: Component Order](../migration/component-order.md)
