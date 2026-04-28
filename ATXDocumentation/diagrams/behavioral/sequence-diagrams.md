# Behavioral Diagrams

> Back to: [README](../../README.md) | [Structural Diagrams](../structural/) | [Architecture Diagrams](../architecture/)

## 1. IPAM Delegation Sequence Diagram

```mermaid
sequenceDiagram
    participant CF as CloudFormation
    participant CR as Custom::IPAM
    participant Lambda as rIpamLambdaDelegate
    participant EC2 as EC2 IPAM API
    participant Orgs as AWS Organizations

    Note over CF: Stack Create
    CF->>CR: Create Custom Resource
    CR->>Lambda: Invoke (RequestType=Create)
    Lambda->>EC2: enable_ipam_organization_admin_account(AccountId)
    EC2->>Orgs: RegisterDelegatedAdministrator
    EC2->>Orgs: EnableAWSServiceAccess
    EC2-->>Lambda: {Success: true}
    Lambda-->>CR: cfnresponse.SUCCESS
    CR-->>CF: Resource Created

    Note over CF: Stack Delete
    CF->>CR: Delete Custom Resource
    CR->>Lambda: Invoke (RequestType=Delete)
    Lambda->>EC2: disable_ipam_organization_admin_account(AccountId)
    EC2->>Orgs: DeregisterDelegatedAdministrator
    EC2-->>Lambda: {Success: true}
    Lambda-->>CR: cfnresponse.SUCCESS
    CR-->>CF: Resource Deleted
```

## 2. VPC Provisioning Sequence Diagram

```mermaid
sequenceDiagram
    participant CF as CloudFormation
    participant CR as Custom::GetIpamPoolId
    participant Lambda as rIpamLambdaGetPoolId
    participant EC2 as EC2 IPAM API
    participant VPC as VPC Service

    Note over CF: Stack Create
    CF->>CR: Create Custom Resource
    CR->>Lambda: Invoke (RequestType=Create)
    Lambda->>Lambda: Read AWS_REGION, ENVIRONMENT env vars
    Lambda->>EC2: describe_ipam_pools(Filters=[locale=region])
    EC2-->>Lambda: IpamPools list
    
    loop For each pool
        Lambda->>Lambda: Check AllocationResourceTags
        alt tag.Value == ENVIRONMENT
            Lambda->>Lambda: Capture IpamPoolId
            Note over Lambda: break
        end
    end
    
    Lambda-->>CR: cfnresponse.SUCCESS {Data: pool_id}
    CR-->>CF: Resource Created (Data=pool_id)
    
    CF->>VPC: Create VPC (IpamPoolId=pool_id, NetmaskLength=N)
    VPC->>EC2: Allocate CIDR from IPAM Pool
    EC2-->>VPC: Allocated CIDR block
    VPC-->>CF: VPC Created
    
    CF->>CF: Create Subnets (Fn::Cidr from VPC CIDR)
    CF->>CF: Create IGW, NAT Gateways, Route Tables
    CF-->>CF: Stack CREATE_COMPLETE
```

## 3. Pool Lookup Lambda Activity Diagram

```
┌─────────────────────┐
│     START            │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────┐
│ Read AWS_REGION and  │
│ ENVIRONMENT env vars │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│ RequestType == 'Create'? │
├──── No ──────────────────┼──▶ ┌────────────────────────┐
│                          │    │ Send cfnresponse.SUCCESS│
│                          │    │ (no-op for Update/Delete)│
│                          │    └────────────────────────┘
└──── Yes ─────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Call describe_ipam_pools()   │
│ Filter: locale = AWS_REGION  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────┐
│ Pools returned?          │
├──── No (empty list) ─────┼──▶ ┌───────────────────┐
│                          │    │ Print "No pools"  │
│                          │    │ status = FAILED   │
│                          │    └────────┬──────────┘
└──── Yes ─────────────────┘             │
           │                              │
           ▼                              │
┌──────────────────────────────┐         │
│ FOR each pool:               │         │
│                              │         │
│  Has AllocationResourceTags? │         │
│  ├── No → print "no tags"   │         │
│  └── Yes ─┐                 │         │
│            ▼                 │         │
│  FOR each tag:               │         │
│    tag.Value == ENVIRONMENT? │         │
│    ├── No → print warning    │         │
│    └── Yes → capture poolId  │         │
│             status = SUCCESS │         │
│             BREAK            │         │
└──────────────┬───────────────┘         │
               │                          │
               ▼                          │
┌──────────────────────────────┐         │
│ Send cfnresponse(status,     │◀────────┘
│   {Data: pool_id})           │
└──────────────────────────────┘
```

---

> See also: [Behavior: Workflows](../../behavior/workflows.md) | [Behavior: Decision Logic](../../behavior/decision-logic.md)
