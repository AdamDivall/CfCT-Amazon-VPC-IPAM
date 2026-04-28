# Dependency Analysis

> Back to: [README](../README.md) | [Code Metrics](code-metrics.md) | [Complexity Analysis](complexity-analysis.md) | [Security Patterns](security-patterns.md) | [Tech Debt](tech-debt.md)

## Internal Dependencies (Deployment Order)

```
┌─────────────────────────────┐
│ 1. vpc-ipam-delegation.yaml │ ← No dependencies (first to deploy)
│    Management Account       │
└─────────────┬───────────────┘
              │ Enables IPAM delegation → Network Account
              ▼
┌─────────────────────────────┐
│ 2. vpc-ipam-pools.yaml      │ ← Depends on Step 1 (delegation active)
│    Network Account          │
└─────────────┬───────────────┘
              │ Creates pools + RAM shares to Organization
              ▼
┌─────────────────────────────┐
│ 3. custom-vpc.yaml          │ ← Depends on Step 2 (pools shared via RAM)
│    Member Accounts          │
└─────────────────────────────┘
```

### Dependency Details

| Source | Target | Dependency Type | Mechanism |
|--------|--------|----------------|-----------|
| `vpc-ipam-pools.yaml` | `vpc-ipam-delegation.yaml` | Prerequisite | IPAM delegation must be enabled before pools can be created in the delegated account |
| `custom-vpc.yaml` | `vpc-ipam-pools.yaml` | Data dependency | Lambda queries IPAM pools that must exist and be shared via RAM |
| `custom-vpc.yaml` | RAM share in pools template | Access dependency | Member accounts must have RAM share accepted to see IPAM pools |

## External Dependencies

### Python Libraries

| Library | Version | Source | Used By | Criticality |
|---------|---------|--------|---------|-------------|
| `boto3` | Bundled with runtime | AWS Lambda | Both Lambdas | Critical |
| `cfnresponse` | Bundled with runtime | AWS Lambda | Both Lambdas | Critical |
| `botocore` | Bundled with runtime (via boto3) | AWS Lambda | Both Lambdas | Critical |
| `os` | Standard library | Python | Pool Lookup Lambda | Low |

**Note:** No external packages are installed. All dependencies are provided by the AWS Lambda Python 3.9 runtime.

### AWS Services

| Service | Used By | API Calls | Criticality |
|---------|---------|-----------|-------------|
| Amazon EC2 (IPAM) | Both Lambdas + VPC template | `EnableIpamOrganizationAdminAccount`, `DisableIpamOrganizationAdminAccount`, `DescribeIpamPools`, VPC/Subnet creation | Critical |
| AWS Organizations | Delegation Lambda | `RegisterDelegatedAdministrator`, `DeregisterDelegatedAdministrator`, `EnableAWSServiceAccess` | Critical |
| AWS IAM | Delegation Lambda | `CreateServiceLinkedRole` | Critical |
| AWS RAM | Pools template | `CreateResourceShare` (implicit via CloudFormation) | Critical |
| CloudWatch Logs | Both Lambdas | Log writing (via Lambda runtime) | Low |
| AWS CloudFormation | All templates | Stack orchestration | Critical |
| CfCT | All templates | Deployment mechanism | Critical |

### AWS Service Dependencies Graph

```
CfCT (Deployment)
  │
  ├── CloudFormation
  │     ├── Lambda
  │     │     ├── EC2 IPAM APIs
  │     │     ├── CloudWatch Logs
  │     │     └── boto3/cfnresponse (runtime)
  │     ├── EC2 (VPC, Subnets, IGW, NAT, EIP, Routes)
  │     ├── IAM (Lambda roles)
  │     └── RAM (Resource sharing)
  │
  └── Organizations (delegation management)
```

## Cross-Template Data Flow

| Data Element | Producer | Consumer | Transfer Mechanism |
|-------------|----------|----------|-------------------|
| Network Account ID | `vpc-ipam-delegation.json` → `pNetworkAccountId` | `vpc-ipam-delegation.yaml` Lambda | CloudFormation parameter → Custom Resource property |
| IPAM Pool IDs | `vpc-ipam-pools.yaml` IPAM Pool resources | `custom-vpc.yaml` Lambda | RAM sharing + `describe_ipam_pools` API |
| Pool locale | `vpc-ipam-pools.yaml` `Locale` property | `custom-vpc.yaml` Lambda | IPAM pool metadata (filter by `AWS_REGION`) |
| Pool environment tags | `vpc-ipam-pools.yaml` `AllocationResourceTags` | `custom-vpc.yaml` Lambda | IPAM pool metadata (match `ENVIRONMENT` env var) |
| Organization ID | `vpc-ipam-pools.json` → `pOrganizationId` | `vpc-ipam-pools.yaml` RAM share | CloudFormation parameter → RAM principal ARN |

## Transitive Dependencies

```
custom-vpc.yaml
  └── IPAM Pool (shared via RAM)
        └── vpc-ipam-pools.yaml
              └── IPAM Delegation (active)
                    └── vpc-ipam-delegation.yaml
                          └── AWS Organizations (service access enabled)
```

The VPC template transitively depends on AWS Organizations being properly configured with IPAM service access enabled, even though it never directly interacts with Organizations.

---

> See also: [Architecture: Dependencies](../architecture/dependencies.md) | [Migration: Component Order](../migration/component-order.md)
