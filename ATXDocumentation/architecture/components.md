# Components

> Back to: [README](../README.md) | [System Overview](system-overview.md) | [Dependencies](dependencies.md) | [Patterns](patterns.md)

## Component Overview

The system consists of three major components, each implemented as a CloudFormation template with optional Lambda-backed Custom Resources.

---

## Component 1: IPAM Delegation

**Template:** `vpc-ipam-delegation.yaml`  
**Parameter File:** `vpc-ipam-delegation.json`  
**Deployment Target:** Management Account (Control Tower home region)

### Purpose
Enables VPC IPAM delegated administration from the Management Account to the Network Account. This is a prerequisite for all other components.

### Resources

| Resource ID | Type | Description |
|-------------|------|-------------|
| `rIpamGetPoolIdLambdaLogGroup` | `AWS::Logs::LogGroup` | CloudWatch Log Group for the delegation Lambda |
| `rIpamLambdaRoleDelegate` | `AWS::IAM::Role` | Execution role for the delegation Lambda |
| `rIpamLambdaDelegate` | `AWS::Lambda::Function` | Lambda that calls `enable/disable_ipam_organization_admin_account` |
| `rIpam` | `Custom::IPAM` | Custom Resource that triggers the delegation Lambda |

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `pNetworkAccountId` | String (12-digit) | AWS Account ID to delegate IPAM admin to |
| `pLambdaLogGroupRetention` | String | Log retention in days |
| `pTagEnvironment` | String | Environment tag (Production/UAT/Development) |

### Lambda Function: `rIpamLambdaDelegate`
- **Handler:** `index.lambda_handler`
- **Runtime:** Python 3.9
- **Memory:** 128 MB
- **Timeout:** 60 seconds
- **Code:** Inline ZipFile
- **Actions:** `ec2:EnableIpamOrganizationAdminAccount`, `ec2:DisableIpamOrganizationAdminAccount`

---

## Component 2: IPAM Pool Configuration

**Template:** `vpc-ipam-pools.yaml`  
**Parameter File:** `vpc-ipam-pools.json`  
**Deployment Target:** Network Account (delegated IPAM admin)

### Purpose
Creates the IPAM instance, scope, and hierarchical pool structure. Shares environment-level pools to the entire organization via AWS RAM.

### Resources

| Resource ID | Type | Description |
|-------------|------|-------------|
| `rIpam` | `AWS::EC2::IPAM` | IPAM instance with operating regions |
| `rIpamScope` | `AWS::EC2::IPAMScope` | Custom private scope |
| `rIpamTopPoolIpv4` | `AWS::EC2::IPAMPool` | Top-level IPv4 pool (3 CIDRs) |
| `rIpamPoolRegional1Ipv4` | `AWS::EC2::IPAMPool` | Region 1 pool |
| `rIpamPoolRegional2Ipv4` | `AWS::EC2::IPAMPool` | Region 2 pool |
| `rIpamPoolRegional1ProdIpv4` | `AWS::EC2::IPAMPool` | Region 1 Production pool |
| `rIpamPoolRegional1UatIpv4` | `AWS::EC2::IPAMPool` | Region 1 UAT pool |
| `rIpamPoolRegional1DevIpv4` | `AWS::EC2::IPAMPool` | Region 1 Development pool |
| `rIpamPoolRegional2ProdIpv4` | `AWS::EC2::IPAMPool` | Region 2 Production pool |
| `rIpamPoolRegional2UatIpv4` | `AWS::EC2::IPAMPool` | Region 2 UAT pool |
| `rIpamPoolRegional2DevIpv4` | `AWS::EC2::IPAMPool` | Region 2 Development pool |
| `rRamShareIpamEnvironmentPoolIpv4` | `AWS::RAM::ResourceShare` | RAM share for all environment pools |

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `pOrganizationId` | String (12-char) | AWS Organizations ID |
| `pManagementAccountId` | String (12-digit) | Management Account ID |
| `pOperatingRegionList` | List\<String\> | AWS Regions for IPAM |
| `pMainPoolCidrIpv4List` | List\<String\> | Top-level CIDRs |
| `pProdPoolCidrIpv4List` | List\<String\> | Production CIDRs per region |
| `pUatPoolCidrIpv4List` | List\<String\> | UAT CIDRs per region |
| `pDevPoolCidrIpv4List` | List\<String\> | Development CIDRs per region |
| `pTagEnvironment` | String | Environment tag |

### Pool Hierarchy
```
Top Pool (3 CIDRs)
├── Region 1 Pool (CIDR[0])
│   ├── Region 1 Production Pool (Locale: Region[0])
│   ├── Region 1 UAT Pool (Locale: Region[0])
│   └── Region 1 Development Pool (Locale: Region[0])
└── Region 2 Pool (CIDR[1])
    ├── Region 2 Production Pool (Locale: Region[1])
    ├── Region 2 UAT Pool (Locale: Region[1])
    └── Region 2 Development Pool (Locale: Region[1])
```

---

## Component 3: Custom VPC

**Template:** `custom-vpc.yaml`  
**Deployment Target:** Member Accounts (any region with IPAM pools)

### Purpose
Creates a VPC with IPAM-allocated CIDR blocks, 3 subnet tiers (Public, Hybrid, Private) across 3 AZs, with Internet Gateway, NAT Gateways, and routing.

### Resources (47 total)

| Category | Resources | Count |
|----------|-----------|-------|
| Lambda & Custom Resource | Log Group, IAM Role, Lambda, Custom Resource | 4 |
| VPC Core | VPC, Internet Gateway, VPC-IGW Attachment | 3 |
| Public Subnets | SubnetA/B/C | 3 |
| Hybrid Subnets | SubnetA/B/C | 3 |
| Private Subnets | SubnetA/B/C | 3 |
| Route Tables | Public (1), Hybrid (3), Private (3) | 7 |
| Routes | Public default (1), Hybrid default (3), Private default (3) | 7 |
| Route Table Associations | Public (3), Hybrid (3), Private (3) | 9 |
| NAT Gateways | EIPs (3) + NAT Gateways (3) | 6 |
| **Total** | | **45** |

### Lambda Function: `rIpamLambdaGetPoolId`
- **Handler:** `index.lambda_handler`
- **Runtime:** Python 3.9
- **Memory:** 128 MB
- **Timeout:** 60 seconds
- **Code:** Inline ZipFile
- **Actions:** `ec2:DescribeIpamPools`
- **Environment Variables:** `ENVIRONMENT` (from `pTagEnvironment`)

---

> See also: [Dependencies](dependencies.md) | [Reference: Program Structure](../reference/program-structure.md)
