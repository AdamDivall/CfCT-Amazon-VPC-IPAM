# Architectural Patterns

> Back to: [README](../README.md) | [System Overview](system-overview.md) | [Components](components.md) | [Dependencies](dependencies.md)

## 1. CloudFormation Custom Resources Pattern

**Used in:** `vpc-ipam-delegation.yaml`, `custom-vpc.yaml`

Both templates use Lambda-backed CloudFormation Custom Resources to invoke AWS API calls that are not natively supported by CloudFormation resource types.

### Pattern Structure
```
CloudFormation Stack Create/Update/Delete
    │
    ▼
Custom::ResourceType (Properties include ServiceToken)
    │
    ▼
AWS Lambda Function (receives CloudFormation event)
    │
    ├── event['RequestType'] == 'Create' → Invoke AWS API
    ├── event['RequestType'] == 'Update' → Invoke AWS API (or no-op)
    └── event['RequestType'] == 'Delete' → Invoke reverse AWS API
    │
    ▼
cfnresponse.send(SUCCESS/FAILED) → CloudFormation continues
```

### Implementation Details
- **`Custom::IPAM`** (delegation template): Calls `enable_ipam_organization_admin_account` on Create/Update and `disable_ipam_organization_admin_account` on Delete
- **`Custom::GetIpamPoolId`** (VPC template): Calls `describe_ipam_pools` on Create, no-ops on Update/Delete. Returns the pool ID as response data

## 2. Delegated Administration Pattern

**Used in:** `vpc-ipam-delegation.yaml`

This pattern follows the AWS best practice of delegating service administration to a dedicated account rather than operating from the Management Account.

### Pattern Flow
```
Management Account
    │
    ├── Lambda calls ec2:EnableIpamOrganizationAdminAccount
    │   with DelegatedAdminAccountId = Network Account ID
    │
    └── Lambda also requires:
        ├── organizations:RegisterDelegatedAdministrator
        ├── organizations:EnableAWSServiceAccess
        └── iam:CreateServiceLinkedRole
```

**Benefits:**
- Reduces operational burden on the Management Account
- Follows principle of least privilege
- Enables Network team self-service for IPAM management

## 3. Hierarchical IPAM Pool Design

**Used in:** `vpc-ipam-pools.yaml`

The IPAM pool hierarchy follows a 3-tier design pattern:

### Tier Structure

| Tier | Purpose | Scope | Count |
|------|---------|-------|-------|
| 1 — Top Pool | Organization-wide CIDR aggregation | Global | 1 |
| 2 — Regional Pools | Per-region CIDR allocation | Region-specific | 2 (per operating region) |
| 3 — Environment Pools | Per-environment CIDR allocation | Region + Environment | 6 (3 envs × 2 regions) |

### Design Characteristics
- **Source Pool Chaining:** Each regional pool sources from the top pool; each environment pool sources from its regional pool
- **Locale Binding:** Environment pools are bound to a specific AWS region via the `Locale` property
- **Allocation Resource Tags:** Environment pools use `AllocationResourceTags` (Key: `Environment`, Value: `Production`/`UAT`/`Development`) for automatic VPC-to-pool matching
- **Auto Import:** All pools have `AutoImport: True` for automatic CIDR discovery

## 4. CfCT Deployment Pattern

**Used by:** All templates (deployment mechanism)

Customizations for Control Tower provides a GitOps-style deployment pattern:

```
manifest.yaml
    │
    ├── deployment_targets: Management Account
    │   └── vpc-ipam-delegation.yaml + vpc-ipam-delegation.json
    │
    ├── deployment_targets: Network Account
    │   └── vpc-ipam-pools.yaml + vpc-ipam-pools.json
    │
    └── deployment_targets: Member Accounts
        └── custom-vpc.yaml (parameters managed per-account)
```

**Characteristics:**
- Templates go in `/templates/` folder
- Parameters go in `/parameters/` folder
- `manifest.yaml` defines deployment targets, regions, and stack names
- Uses CloudFormation StackSets under the hood

## 5. Three-Tier VPC Subnet Pattern

**Used in:** `custom-vpc.yaml`

The VPC is structured with three subnet tiers across three Availability Zones:

| Tier | Subnets | Internet Access | Use Case |
|------|---------|-----------------|----------|
| Public | 3 (A, B, C) | Direct via Internet Gateway | Load balancers, bastion hosts |
| Hybrid | 3 (A, B, C) | Outbound via NAT Gateway | Application servers |
| Private | 3 (A, B, C) | None (routes via NAT) | Databases, internal services |

**CIDR Allocation:** Uses `Fn::Cidr` with size mappings (Small/Medium/Large) to calculate subnet CIDRs from the VPC CIDR block.

## Anti-Patterns Identified

| Anti-Pattern | Location | Description |
|--------------|----------|-------------|
| Inline Lambda Code | `vpc-ipam-delegation.yaml`, `custom-vpc.yaml` | Lambda code in CloudFormation `ZipFile` is hard to test and version |
| Code Duplication | `lambda/` dir + `vpc-ipam-delegation.yaml` | Same code exists in two places |
| Hardcoded Scale | `vpc-ipam-pools.yaml` | Region count hardcoded to 2 via `!Select` indices |
| Missing Outputs | All templates | No CloudFormation Outputs defined |

---

> See also: [Behavior: Workflows](../behavior/workflows.md) | [Analysis: Complexity](../analysis/complexity-analysis.md)
