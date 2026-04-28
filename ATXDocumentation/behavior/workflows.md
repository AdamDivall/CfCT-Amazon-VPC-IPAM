> ⚠️ **Early Access**: Behavior documentation is in early access. Please review critically.

# Workflows

> Back to: [README](../README.md) | [Business Logic](business-logic.md) | [Decision Logic](decision-logic.md) | [Error Handling](error-handling.md)

## Overview

This document describes the application-level workflows implemented by the project. Only business/infrastructure workflows are documented here — build, CI/CD, and test workflows are excluded.

---

## Workflow 1: IPAM Delegation Workflow

**Template:** `vpc-ipam-delegation.yaml`  
**Deployed To:** Management Account  
**Purpose:** Enable/disable IPAM delegated administration

### Stack Creation Flow

```
CloudFormation Stack Create
    │
    ▼
1. Create rIpamLambdaRoleDelegate (IAM Role)
    │
    ▼
2. Create rIpamLambdaDelegate (Lambda Function)
    │
    ▼
3. Create rIpamGetPoolIdLambdaLogGroup (CloudWatch Log Group)
    │
    ▼
4. Create rIpam (Custom::IPAM)
    │
    ├── Invokes Lambda with RequestType='Create'
    │
    ▼
5. Lambda calls ec2.enable_ipam_organization_admin_account()
    │
    ├── Success → cfnresponse.SUCCESS → Stack CREATE_COMPLETE
    └── Failure → cfnresponse.FAILED → Stack ROLLBACK
```

### Stack Deletion Flow

```
CloudFormation Stack Delete
    │
    ▼
1. Delete rIpam (Custom::IPAM)
    │
    ├── Invokes Lambda with RequestType='Delete'
    │
    ▼
2. Lambda calls ec2.disable_ipam_organization_admin_account()
    │
    ├── Success → cfnresponse.SUCCESS → Continue deletion
    └── Failure → cfnresponse.FAILED → Stack DELETE_FAILED
    │
    ▼
3. Delete rIpamLambdaDelegate, rIpamLambdaRoleDelegate, rIpamGetPoolIdLambdaLogGroup
```

---

## Workflow 2: IPAM Pool Hierarchy Setup Workflow

**Template:** `vpc-ipam-pools.yaml`  
**Deployed To:** Network Account (after delegation is active)  
**Purpose:** Create the complete IPAM pool hierarchy and RAM shares

### Stack Creation Flow

```
CloudFormation Stack Create
    │
    ▼
1. Create rIpam (AWS::EC2::IPAM)
    │  - Configures operating regions (3 regions from pOperatingRegionList)
    │
    ▼
2. Create rIpamScope (AWS::EC2::IPAMScope)
    │  - Custom private scope within the IPAM
    │
    ▼
3. Create rIpamTopPoolIpv4 (AWS::EC2::IPAMPool)
    │  - Top-level pool with 3 provisioned CIDRs
    │
    ├──────────────────────┐
    ▼                      ▼
4a. Create                4b. Create
    rIpamPoolRegional1Ipv4    rIpamPoolRegional2Ipv4
    (Region 1 Pool)           (Region 2 Pool)
    │                         │
    ├───┬───┐                 ├───┬───┐
    ▼   ▼   ▼                 ▼   ▼   ▼
5a. Region1  5b. Region1  5c. Region1  5d. Region2  5e. Region2  5f. Region2
    Prod         UAT          Dev          Prod         UAT          Dev
    Pool         Pool         Pool         Pool         Pool         Pool
    │            │            │            │            │            │
    └────────────┴────────────┴────────────┴────────────┴────────────┘
                              │
                              ▼
6. Create rRamShareIpamEnvironmentPoolIpv4 (AWS::RAM::ResourceShare)
   - Shares all environment pools to the Organization
```

### Key Dependencies
- IPAM must be created before Scope
- Scope must be created before Top Pool
- Top Pool must be created before Regional Pools
- Regional Pools must be created before Environment Pools
- All Environment Pools must be created before RAM Share

---

## Workflow 3: VPC Provisioning Workflow

**Template:** `custom-vpc.yaml`  
**Deployed To:** Member Accounts  
**Purpose:** Create a VPC with IPAM-allocated CIDR and full networking stack

### Stack Creation Flow

```
CloudFormation Stack Create
    │
    ▼
1. Create rIpamLambdaRoleGetPoolId (IAM Role)
    │
    ▼
2. Create rIpamLambdaGetPoolId (Lambda Function)
    │  - Environment: ENVIRONMENT = pTagEnvironment
    │
    ▼
3. Create rIpamGetPoolIdLambdaLogGroup (CloudWatch Log Group)
    │
    ▼
4. Create rCustomGetPoolId (Custom::GetIpamPoolId)
    │
    ├── Invokes Lambda with RequestType='Create'
    │
    ▼
5. Lambda queries IPAM pools:
    │  a. Filter by locale = AWS_REGION
    │  b. Match AllocationResourceTags where Value == ENVIRONMENT
    │  c. Return matching Pool ID as responseData['Data']
    │
    ▼
6. Create rVpc (AWS::EC2::VPC)
    │  - Ipv4IpamPoolId = Pool ID from step 5
    │  - Ipv4NetmaskLength = from mVpcSize mapping
    │  - IPAM allocates next available CIDR
    │
    ▼
7. Create rInternetGateway + rVpcGatewayAttachment
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
8a. Public Subnets  8b. Hybrid Subnets  8c. Private Subnets
    (A, B, C)           (A, B, C)           (A, B, C)
    │                   │                   │
    ▼                   ▼                   ▼
9a. Route Tables    9b. Route Tables    9c. Route Tables
    │                   │                   │
    ▼                   ▼                   ▼
10a. EIPs + NAT Gateways (A, B, C)
    │
    ▼
11. Routes: Public → IGW, Hybrid → NAT, Private → NAT
    │
    ▼
12. Route Table Associations
    │
    ▼
Stack CREATE_COMPLETE
```

### Key Networking Design
- **Public subnets** route to Internet Gateway (direct internet access)
- **Hybrid subnets** route to NAT Gateways (outbound-only internet)
- **Private subnets** route to NAT Gateways (outbound-only internet)
- Each AZ has its own NAT Gateway for high availability
- Hybrid and Private subnets have per-AZ route tables for independent NAT routing

---

> See also: [Architecture: Patterns](../architecture/patterns.md) | [Diagrams: Behavioral](../diagrams/behavioral/)
