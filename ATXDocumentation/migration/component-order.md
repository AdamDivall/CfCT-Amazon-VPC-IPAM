# Component Migration Order

> Back to: [README](../README.md) | [Test Specifications](test-specifications.md) | [Validation Criteria](validation-criteria.md)

## Overview

This document defines the order in which components should be migrated, updated, or redeployed. The deployment order is critical due to dependencies between templates.

## Deployment Sequence

```
Step 1 ──▶ Step 2 ──▶ Step 3
```

### Step 1: IPAM Delegation (vpc-ipam-delegation.yaml)

**Deploy to:** Management Account  
**Region:** Control Tower home region only  
**Priority:** First — no dependencies

| Item | Details |
|------|---------|
| Template | `vpc-ipam-delegation.yaml` |
| Parameters | `vpc-ipam-delegation.json` |
| Account | Management Account |
| Region | CT home region |
| CfCT Method | `stack_set` |
| Prerequisites | CfCT deployed, Network Account exists |
| Blocks | Step 2 (pools template) |

**Migration Notes:**
- This stack creates a Lambda function and Custom Resource in the Management Account
- Must complete successfully before Step 2 can begin
- If updating Python runtime, update this template first

### Step 2: IPAM Pool Configuration (vpc-ipam-pools.yaml)

**Deploy to:** Network Account  
**Region:** Control Tower home region (IPAM manages multiple regions from a single region)  
**Priority:** Second — depends on Step 1

| Item | Details |
|------|---------|
| Template | `vpc-ipam-pools.yaml` |
| Parameters | `vpc-ipam-pools.json` |
| Account | Network Account (delegated IPAM admin) |
| Region | CT home region |
| CfCT Method | `stack_set` |
| Prerequisites | Step 1 complete, IPAM delegation active |
| Blocks | Step 3 (VPC template) |

**Migration Notes:**
- ⚠️ Fix RAM share Region 3 references before deployment
- IPAM pools must be created and RAM shared before member accounts can use them
- Pool changes require careful validation to avoid disrupting existing VPC allocations

### Step 3: Custom VPC (custom-vpc.yaml)

**Deploy to:** Member Accounts  
**Region:** Any region with IPAM pools configured  
**Priority:** Third — depends on Step 2

| Item | Details |
|------|---------|
| Template | `custom-vpc.yaml` |
| Parameters | Per-account configuration |
| Account | Member Accounts |
| Region | Regions matching IPAM pool locales |
| CfCT Method | `stack_set` |
| Prerequisites | Step 2 complete, IPAM pools shared via RAM |
| Blocks | None |

**Migration Notes:**
- Can be deployed to multiple accounts in parallel
- Each deployment allocates a CIDR from the IPAM pool — ensure pool capacity
- ⚠️ Add `UAT` to `pTagEnvironment` AllowedValues if UAT deployments are needed

## Dependency Matrix

| Component | Depends On | Depended On By |
|-----------|-----------|----------------|
| vpc-ipam-delegation.yaml | None | vpc-ipam-pools.yaml |
| vpc-ipam-pools.yaml | vpc-ipam-delegation.yaml | custom-vpc.yaml |
| custom-vpc.yaml | vpc-ipam-pools.yaml | None |

## Rollback Order

If a rollback is needed, reverse the deployment order:

1. Delete `custom-vpc.yaml` stacks from member accounts (releases IPAM allocations)
2. Delete `vpc-ipam-pools.yaml` stack from Network Account (removes IPAM pools and RAM share)
3. Delete `vpc-ipam-delegation.yaml` stack from Management Account (revokes IPAM delegation)

**⚠️ Warning:** Deleting VPC stacks will destroy all networking resources in those accounts. Ensure no workloads depend on the VPCs before rolling back.

---

> See also: [Architecture: Dependencies](../architecture/dependencies.md) | [Analysis: Dependency Analysis](../analysis/dependency-analysis.md)
