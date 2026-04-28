# Dependencies

> Back to: [README](../README.md) | [System Overview](system-overview.md) | [Components](components.md) | [Patterns](patterns.md)

## Deployment Order (Internal Dependencies)

The three CloudFormation templates must be deployed in a strict order:

```
1. vpc-ipam-delegation.yaml  (Management Account)
        │
        ▼  Enables delegated admin → Network Account
2. vpc-ipam-pools.yaml       (Network Account)
        │
        ▼  Creates IPAM pools + RAM shares
3. custom-vpc.yaml           (Member Accounts)
```

| Step | Template | Depends On | Reason |
|------|----------|------------|--------|
| 1 | `vpc-ipam-delegation.yaml` | None | First deployment — delegates IPAM admin |
| 2 | `vpc-ipam-pools.yaml` | Step 1 complete | Requires IPAM delegation to be active in Network Account |
| 3 | `custom-vpc.yaml` | Step 2 complete | Requires IPAM pools to exist and be shared via RAM |

## External Dependencies

### AWS Services

| Service | Used By | Purpose |
|---------|---------|---------|
| AWS Lambda | `vpc-ipam-delegation.yaml`, `custom-vpc.yaml` | Custom Resource compute |
| Amazon EC2 (IPAM APIs) | All templates | IPAM management and VPC creation |
| AWS Organizations | `vpc-ipam-delegation.yaml` | Delegated admin registration |
| AWS RAM | `vpc-ipam-pools.yaml` | Cross-account IPAM pool sharing |
| AWS IAM | `vpc-ipam-delegation.yaml`, `custom-vpc.yaml` | Lambda execution roles |
| CloudWatch Logs | `vpc-ipam-delegation.yaml`, `custom-vpc.yaml` | Lambda log storage |
| AWS CloudFormation | All templates | Infrastructure orchestration |
| CfCT (Customizations for Control Tower) | Deployment mechanism | StackSet-based multi-account deployment |

### Python Libraries

| Library | Source | Used In |
|---------|--------|---------|
| `boto3` | Bundled with Lambda runtime | Both Lambda functions |
| `cfnresponse` | Bundled with Lambda runtime | Both Lambda functions |
| `botocore.exceptions` | Bundled with Lambda runtime (via boto3) | Both Lambda functions |
| `os` | Python standard library | Pool lookup Lambda only |

### AWS API Calls

| API Call | Template | Lambda Function |
|----------|----------|-----------------|
| `ec2:EnableIpamOrganizationAdminAccount` | `vpc-ipam-delegation.yaml` | `rIpamLambdaDelegate` |
| `ec2:DisableIpamOrganizationAdminAccount` | `vpc-ipam-delegation.yaml` | `rIpamLambdaDelegate` |
| `ec2:DescribeIpamPools` | `custom-vpc.yaml` | `rIpamLambdaGetPoolId` |

## Internal Cross-Template Data Flow

```
vpc-ipam-delegation.yaml                vpc-ipam-pools.yaml              custom-vpc.yaml
┌──────────────────────┐   ┌───────────────────────────┐   ┌──────────────────────────┐
│ pNetworkAccountId ───┼──▶│ Deployed in this account  │   │                          │
│                      │   │                           │   │                          │
│ Lambda enables IPAM  │   │ IPAM + Pools created      │   │ Lambda queries IPAM      │
│ delegation           │   │ RAM Share → Organization  ├──▶│ pools by locale +        │
│                      │   │                           │   │ AllocationResourceTags   │
│                      │   │ Pool AllocationResource   │   │                          │
│                      │   │ Tags: Environment=Prod/   │   │ VPC uses pool CIDR       │
│                      │   │ UAT/Dev                   │   │                          │
└──────────────────────┘   └───────────────────────────┘   └──────────────────────────┘
```

**Key cross-template relationships:**
- `vpc-ipam-delegation.yaml` sends the `pNetworkAccountId` which becomes the account where `vpc-ipam-pools.yaml` is deployed
- `vpc-ipam-pools.yaml` creates IPAM pools with `AllocationResourceTags` (key: `Environment`) and `Locale` (region) that are queried by the Lambda in `custom-vpc.yaml`
- The RAM share in `vpc-ipam-pools.yaml` makes the pools visible to member accounts running `custom-vpc.yaml`

## Build Tool Dependencies

This project has no build tools. CloudFormation templates and JSON parameter files are deployed directly via CfCT without a build step.

---

> See also: [Analysis: Dependency Analysis](../analysis/dependency-analysis.md) | [Migration: Component Order](../migration/component-order.md)
