# Infrastructure & CloudFormation Patterns

> Back to: [README](../README.md)

## Overview

This document captures specialized infrastructure and deployment patterns found in the CfCT Amazon VPC IPAM project.

---

## 1. CfCT Manifest Configuration

The project is designed for deployment via Customizations for Control Tower (CfCT). The `manifest.yaml` configuration follows this pattern:

```yaml
- name: Enable-VPC-IPAM-Delegated-Admin
  description: "CloudFormation Template to Enable Delegated Administration of VPC IPAM"
  resource_file: templates/vpc-ipam-delegation.yaml
  parameter_file: parameters/vpc-ipam-delegation.json
  deploy_method: stack_set
  deployment_targets:
    accounts:
      - <Management Account ID or Logical Name>
  regions:
    - <Control Tower Home Region>

- name: Configure-VPC-IPAM-Pools
  description: "CloudFormation Template to Configure VPC IPAM Pools"
  resource_file: templates/vpc-ipam-pools.yaml
  parameter_file: parameters/vpc-ipam-pools.json
  deploy_method: stack_set
  deployment_targets:
    accounts:
      - <Network Account ID or Logical Name>
  regions:
    - <Control Tower Home Region>
```

### Key Configuration Points
- **deploy_method:** `stack_set` — uses CloudFormation StackSets for deployment
- **deployment_targets:** Account-specific targeting (Management vs Network Account)
- **regions:** Single region for IPAM (manages multi-region from a single region)
- **File paths:** Templates in `/templates/`, parameters in `/parameters/`

## 2. CloudFormation Inline Lambda (ZipFile) Pattern

Both Lambda functions use the `ZipFile` property for inline code:

```yaml
Code:
  ZipFile: |
    import boto3
    import cfnresponse
    # ... code ...
```

### Characteristics
- **Handler:** Must use `index.lambda_handler` (ZipFile creates an `index.py` file)
- **Size limit:** 4,096 bytes (ZipFile maximum)
- **Dependencies:** Limited to Lambda runtime bundled packages (no pip install)
- **Versioning:** Code changes tracked in CloudFormation template version control
- **Testing:** Cannot be unit tested independently from the CloudFormation template

### When to Use ZipFile vs S3
| Criteria | ZipFile | S3 |
|----------|---------|-----|
| Code size | < 4KB | > 4KB |
| Dependencies | Runtime-only | Custom packages |
| Testing | Difficult | Standard pytest |
| Deployment | Inline in template | Separate build/upload step |
| Version tracking | Git (template) | S3 versioning |

## 3. CloudFormation Custom Resource Response Pattern

The `cfnresponse` module provides the standard response pattern:

```python
# Success response
cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)

# Failure response
cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
```

### Response Protocol
1. Lambda receives event with `ResponseURL` (pre-signed S3 URL)
2. Lambda performs its work
3. Lambda sends HTTP PUT to `ResponseURL` with status
4. CloudFormation reads the response from S3 and continues

### Failure Modes
- If Lambda crashes without sending a response, CloudFormation waits for the Custom Resource timeout
- Default Custom Resource timeout: 1 hour
- Lambda timeout in this project: 60 seconds

## 4. IPAM Pool Allocation Tag Pattern

IPAM pools use `AllocationResourceTags` for automatic VPC-to-pool matching:

```yaml
AllocationResourceTags:
  - Key: Environment
    Value: Production
```

When a VPC is created with `Ipv4IpamPoolId`, IPAM uses these tags to validate that the VPC's tags match the pool's allocation tags. This enables automatic pool selection in multi-environment setups.

## 5. CloudFormation Fn::Cidr Subnet Calculation Pattern

The VPC template uses `Fn::Cidr` for dynamic subnet sizing:

```yaml
CidrBlock: !Select [ <index>, !Cidr [ !GetAtt rVpc.CidrBlock, 9, !FindInMap [mVpcSize, !Ref pVpcSize, <tier>Cidr]]]
```

### Pattern Breakdown
1. `!GetAtt rVpc.CidrBlock` — Gets the IPAM-allocated VPC CIDR (e.g., `10.0.0.0/22`)
2. `!Cidr [ ..., 9, <bits> ]` — Splits the CIDR into 9 subnets with `<bits>` host bits
3. `!FindInMap [mVpcSize, ...]` — Looks up the subnet bit size from the mapping
4. `!Select [ <index>, ... ]` — Selects the specific subnet by index (0-8)

This avoids hardcoding subnet CIDRs and scales with the VPC size tier.

## 6. Resource Naming Conventions

| Prefix | Meaning | Examples |
|--------|---------|---------|
| `r` | Resource | `rVpc`, `rIpam`, `rNatGatewayA` |
| `p` | Parameter | `pNetworkAccountId`, `pVpcSize` |
| `m` | Mapping | `mVpcSize` |

## 7. Multi-AZ High Availability Pattern

The VPC template deploys resources across 3 Availability Zones:
- 3 Public subnets (one per AZ)
- 3 Hybrid subnets (one per AZ) with individual NAT Gateways
- 3 Private subnets (one per AZ) with individual NAT Gateways
- Per-AZ route tables for Hybrid and Private tiers (enables AZ-independent routing)

This ensures that a single AZ failure doesn't impact all subnet tiers.

---

> See also: [Architecture: Patterns](../architecture/patterns.md) | [Reference: API Reference](../reference/api-reference.md)
