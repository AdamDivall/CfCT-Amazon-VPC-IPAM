# Structural Diagrams

> Back to: [README](../../README.md) | [Behavioral Diagrams](../behavioral/) | [Architecture Diagrams](../architecture/)

## 1. CloudFormation Template Component Diagram

```mermaid
graph TB
    subgraph "vpc-ipam-delegation.yaml (Management Account)"
        D_LOG[rIpamGetPoolIdLambdaLogGroup<br/>AWS::Logs::LogGroup]
        D_ROLE[rIpamLambdaRoleDelegate<br/>AWS::IAM::Role]
        D_LAMBDA[rIpamLambdaDelegate<br/>AWS::Lambda::Function]
        D_CR[rIpam<br/>Custom::IPAM]
        
        D_ROLE --> D_LAMBDA
        D_LAMBDA --> D_LOG
        D_LAMBDA --> D_CR
    end

    subgraph "vpc-ipam-pools.yaml (Network Account)"
        P_IPAM[rIpam<br/>AWS::EC2::IPAM]
        P_SCOPE[rIpamScope<br/>AWS::EC2::IPAMScope]
        P_TOP[rIpamTopPoolIpv4<br/>AWS::EC2::IPAMPool]
        P_R1[rIpamPoolRegional1Ipv4]
        P_R2[rIpamPoolRegional2Ipv4]
        P_R1P[Region1 Prod]
        P_R1U[Region1 UAT]
        P_R1D[Region1 Dev]
        P_R2P[Region2 Prod]
        P_R2U[Region2 UAT]
        P_R2D[Region2 Dev]
        P_RAM[rRamShareIpamEnvironmentPoolIpv4<br/>AWS::RAM::ResourceShare]
        
        P_IPAM --> P_SCOPE
        P_SCOPE --> P_TOP
        P_TOP --> P_R1
        P_TOP --> P_R2
        P_R1 --> P_R1P
        P_R1 --> P_R1U
        P_R1 --> P_R1D
        P_R2 --> P_R2P
        P_R2 --> P_R2U
        P_R2 --> P_R2D
        P_R1P --> P_RAM
        P_R1U --> P_RAM
        P_R1D --> P_RAM
        P_R2P --> P_RAM
        P_R2U --> P_RAM
        P_R2D --> P_RAM
    end

    subgraph "custom-vpc.yaml (Member Accounts)"
        V_LOG[rIpamGetPoolIdLambdaLogGroup]
        V_ROLE[rIpamLambdaRoleGetPoolId]
        V_LAMBDA[rIpamLambdaGetPoolId]
        V_CR[rCustomGetPoolId]
        V_VPC[rVpc]
        V_IGW[rInternetGateway]
        V_SUB["9 Subnets (3 tiers × 3 AZs)"]
        V_RT["7 Route Tables"]
        V_NAT["3 NAT Gateways + 3 EIPs"]
        
        V_ROLE --> V_LAMBDA
        V_LAMBDA --> V_LOG
        V_LAMBDA --> V_CR
        V_CR --> V_VPC
        V_VPC --> V_IGW
        V_VPC --> V_SUB
        V_SUB --> V_RT
        V_SUB --> V_NAT
    end

    D_CR -.->|"Enables delegation"| P_IPAM
    P_RAM -.->|"Shares pools via RAM"| V_CR
```

## 2. IPAM Pool Hierarchy Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    IPAM Instance (rIpam)                          │
│                    Operating Regions: [R1, R2, R3]               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              IPAM Scope (rIpamScope)                      │    │
│  │              Type: private                                │    │
│  │                                                           │    │
│  │  ┌──────────────────────────────────────────────────┐    │    │
│  │  │         Top Pool (rIpamTopPoolIpv4)               │    │    │
│  │  │         CIDRs: [CIDR[0], CIDR[1], CIDR[2]]      │    │    │
│  │  │         AddressFamily: ipv4                       │    │    │
│  │  │                                                    │    │    │
│  │  │  ┌─────────────────┐  ┌─────────────────┐        │    │    │
│  │  │  │ Region 1 Pool   │  │ Region 2 Pool   │        │    │    │
│  │  │  │ CIDR: CIDR[0]   │  │ CIDR: CIDR[1]   │        │    │    │
│  │  │  │                 │  │                  │        │    │    │
│  │  │  │ ┌─────┐ ┌─────┐│  │ ┌─────┐ ┌─────┐ │        │    │    │
│  │  │  │ │Prod │ │UAT  ││  │ │Prod │ │UAT  │ │        │    │    │
│  │  │  │ │Pool │ │Pool ││  │ │Pool │ │Pool │ │        │    │    │
│  │  │  │ └─────┘ └─────┘│  │ └─────┘ └─────┘ │        │    │    │
│  │  │  │ ┌─────┐        │  │ ┌─────┐         │        │    │    │
│  │  │  │ │Dev  │        │  │ │Dev  │         │        │    │    │
│  │  │  │ │Pool │        │  │ │Pool │         │        │    │    │
│  │  │  │ └─────┘        │  │ └─────┘         │        │    │    │
│  │  │  └─────────────────┘  └─────────────────┘        │    │    │
│  │  └──────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## 3. VPC Network Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VPC (IPAM-allocated CIDR)                    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Internet Gateway                          │    │
│  └─────────┬───────────────────┬───────────────────┬───────────┘    │
│            │                   │                   │                 │
│  ┌─────────▼─────┐  ┌─────────▼─────┐  ┌─────────▼─────┐         │
│  │ Public Sub A  │  │ Public Sub B  │  │ Public Sub C  │         │
│  │ (AZ-a)       │  │ (AZ-b)       │  │ (AZ-c)       │         │
│  │ Route: IGW   │  │ Route: IGW   │  │ Route: IGW   │         │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘         │
│          │                   │                   │                  │
│  ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐         │
│  │ NAT GW A     │  │ NAT GW B     │  │ NAT GW C     │         │
│  │ (EIP A)      │  │ (EIP B)      │  │ (EIP C)      │         │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘         │
│          │                   │                   │                  │
│  ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐         │
│  │ Hybrid Sub A │  │ Hybrid Sub B │  │ Hybrid Sub C │         │
│  │ (AZ-a)      │  │ (AZ-b)      │  │ (AZ-c)      │         │
│  │ Route: NAT-A│  │ Route: NAT-B│  │ Route: NAT-C│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Private Sub A│  │ Private Sub B│  │ Private Sub C│         │
│  │ (AZ-a)      │  │ (AZ-b)      │  │ (AZ-c)      │         │
│  │ Route: NAT-A│  │ Route: NAT-B│  │ Route: NAT-C│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

---

> See also: [Architecture: Components](../../architecture/components.md) | [Reference: Data Models](../../reference/data-models.md)
