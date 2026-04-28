# Data Models

> Back to: [README](../README.md) | [Program Structure](program-structure.md) | [Interfaces](interfaces.md) | [API Reference](api-reference.md) | [Modules](modules.md)

## CloudFormation Parameter Types

### String Parameters with Validation

| Parameter | Template | Pattern/Values | Description |
|-----------|----------|----------------|-------------|
| `pNetworkAccountId` | delegation | `^[0-9]{12}$` | 12-digit AWS Account ID |
| `pOrganizationId` | pools | `^[o][\-][a-z0-9]{10}$` | AWS Organization ID (e.g., `o-abc1234567`) |
| `pManagementAccountId` | pools | `^[0-9]{12}$` | 12-digit Management Account ID |
| `pTagEnvironment` | delegation, pools | `Production\|UAT\|Development` | SDLC environment name |
| `pTagEnvironment` | custom-vpc | `Production\|Development` | SDLC environment name (⚠️ missing UAT) |
| `pVpcSize` | custom-vpc | `Small\|Medium\|Large` | VPC sizing tier |
| `pLambdaLogGroupRetention` | delegation, custom-vpc | Enumerated integers | CloudWatch log retention days |

### List Parameters

| Parameter | Template | Expected Format |
|-----------|----------|-----------------|
| `pOperatingRegionList` | pools | Comma-separated AWS regions (e.g., `us-east-1,eu-west-1,ap-southeast-1`) |
| `pMainPoolCidrIpv4List` | pools | Comma-separated CIDRs (e.g., `10.0.0.0/8,172.16.0.0/12,192.168.0.0/16`) |
| `pProdPoolCidrIpv4List` | pools | Comma-separated CIDRs per region |
| `pUatPoolCidrIpv4List` | pools | Comma-separated CIDRs per region |
| `pDevPoolCidrIpv4List` | pools | Comma-separated CIDRs per region |

## VPC Size Mappings (`custom-vpc.yaml`)

The `mVpcSize` mapping defines subnet CIDR sizes for each VPC size tier:

| VPC Size | VPC Netmask (`VpcCidr`) | Public Subnet Bits (`PublicCidr`) | Hybrid Subnet Bits (`HybridCidr`) | Private Subnet Bits (`PrivateCidr`) |
|----------|------------------------|----------------------------------|-----------------------------------|-------------------------------------|
| Small | /22 (1,024 IPs) | 4 bits (16 IPs/subnet) | 6 bits (64 IPs/subnet) | 6 bits (64 IPs/subnet) |
| Medium | /20 (4,096 IPs) | 4 bits (16 IPs/subnet) | 8 bits (256 IPs/subnet) | 8 bits (256 IPs/subnet) |
| Large | /19 (8,192 IPs) | 4 bits (16 IPs/subnet) | 9 bits (512 IPs/subnet) | 9 bits (512 IPs/subnet) |

**CIDR Calculation:**
The template uses `Fn::Cidr` to subdivide the VPC CIDR into 9 subnets:
- Subnets 0–2: Public (A, B, C)
- Subnets 3–5: Hybrid (A, B, C)
- Subnets 6–8: Private (A, B, C)

## IPAM Pool Hierarchy Data Model

```
┌─────────────────────────────────────────────┐
│           Top Pool (rIpamTopPoolIpv4)        │
│  AddressFamily: ipv4                         │
│  AutoImport: True                            │
│  Scope: rIpamScope                           │
│  ProvisionedCidrs: [CIDR[0], CIDR[1],       │
│                     CIDR[2]]                 │
├──────────────────┬──────────────────────────┤
│                  │                           │
▼                  ▼                           │
┌────────────┐  ┌────────────┐                │
│ Region 1   │  │ Region 2   │                │
│ Pool       │  │ Pool       │                │
│ CIDR[0]    │  │ CIDR[1]    │                │
├────────────┤  ├────────────┤                │
│            │  │            │                │
▼   ▼   ▼   │  ▼   ▼   ▼   │                │
Prod UAT Dev │  Prod UAT Dev │                │
Pool Pool Pool  Pool Pool Pool                │
└─────────────────────────────────────────────┘
```

### Pool Properties

| Property | Top Pool | Regional Pool | Environment Pool |
|----------|----------|---------------|------------------|
| `AddressFamily` | ipv4 | ipv4 | ipv4 |
| `AutoImport` | True | True | True |
| `SourceIpamPoolId` | — | Top Pool | Regional Pool |
| `Locale` | — | — | Operating Region |
| `AllocationResourceTags` | — | — | `Environment: Production/UAT/Development` |
| `ProvisionedCidrs` | 3 CIDRs | 1 CIDR | 1 CIDR |

## JSON Parameter File Schema

Both `.json` parameter files follow the CfCT parameter format:

```json
[
  {
    "ParameterKey": "string",
    "ParameterValue": "string"
  }
]
```

This is a JSON array of objects with `ParameterKey` and `ParameterValue` string properties, compatible with the AWS CloudFormation `create-stack`/`update-stack` parameter format.

---

> See also: [Architecture: Components](../architecture/components.md) | [Behavior: Decision Logic](../behavior/decision-logic.md)
