# Program Structure

> Back to: [README](../README.md) | [Interfaces](interfaces.md) | [Data Models](data-models.md) | [API Reference](api-reference.md) | [Modules](modules.md)

## Repository File Listing

```
CfCT-Amazon-VPC-IPAM/
├── lambda/
│   └── lambda-vpc-ipam-delegation.py    # Standalone Lambda handler (34 LOC)
├── vpc-ipam-delegation.yaml             # CloudFormation: IPAM delegation (131 LOC)
├── vpc-ipam-delegation.json             # Parameters for delegation template (13 LOC)
├── vpc-ipam-pools.yaml                  # CloudFormation: IPAM pools + RAM share (265 LOC)
├── vpc-ipam-pools.json                  # Parameters for pools template (33 LOC)
├── custom-vpc.yaml                      # CloudFormation: VPC provisioning (449 LOC)
└── readme.md                            # Project documentation (116 LOC)
```

**Total:** 7 files, 1,041 lines (including readme)

## File Descriptions

### `lambda/lambda-vpc-ipam-delegation.py` (34 lines)

Standalone Python file containing the IPAM delegation Lambda handler. This file is a **duplicate** of the inline code in `vpc-ipam-delegation.yaml` and is not directly referenced by any CloudFormation template.

**Functions:**
- `lambda_handler(event, context)` — Handles CloudFormation Custom Resource events for enabling/disabling IPAM delegated administration

**Imports:** `boto3`, `cfnresponse`, `botocore.exceptions.ClientError`

**Module-level variables:**
- `ec2_client` — boto3 EC2 client instance

### `vpc-ipam-delegation.yaml` (131 lines)

CloudFormation template that delegates IPAM administration to the Network Account. Deployed to the Management Account.

**Sections:**
- `Metadata` — CloudFormation Interface parameter grouping (lines 3–16)
- `Parameters` — 3 parameters (lines 18–39)
- `Resources` — 4 resources (lines 41–131)

### `vpc-ipam-delegation.json` (13 lines)

JSON parameter file for `vpc-ipam-delegation.yaml` used by CfCT. Contains 3 parameter key-value pairs with empty default values.

### `vpc-ipam-pools.yaml` (265 lines)

CloudFormation template that creates the IPAM instance, scope, hierarchical pools, and RAM share. Deployed to the Network Account.

**Sections:**
- `Metadata` — CloudFormation Interface parameter grouping (lines 3–18)
- `Parameters` — 8 parameters (lines 19–61)
- `Resources` — 12 resources (lines 62–265)

### `vpc-ipam-pools.json` (33 lines)

JSON parameter file for `vpc-ipam-pools.yaml` used by CfCT. Contains 8 parameter key-value pairs with empty default values.

### `custom-vpc.yaml` (449 lines)

CloudFormation template that creates a VPC with IPAM-allocated CIDRs, 9 subnets (3 tiers × 3 AZs), routing, and NAT gateways. Deployed to member accounts.

**Sections:**
- `Metadata` — CloudFormation Interface parameter grouping (lines 3–18)
- `Parameters` — 3 parameters (lines 19–43) + unreferenced TGW parameters in metadata
- `Mappings` — VPC size mappings (lines 44–58)
- `Resources` — 45 resources (lines 59–449)

### `readme.md` (116 lines)

Project README with installation instructions for CfCT deployment, parameter descriptions, and `manifest.yaml` configuration examples.

## Code Statistics

| Category | Files | Lines | Percentage |
|----------|-------|-------|------------|
| CloudFormation Templates | 3 | 845 | 81.2% |
| JSON Parameters | 2 | 46 | 4.4% |
| Python | 1 | 34 | 3.3% |
| Documentation | 1 | 116 | 11.1% |
| **Total** | **7** | **1,041** | **100%** |

---

> See also: [Architecture: Components](../architecture/components.md) | [Modules](modules.md)
