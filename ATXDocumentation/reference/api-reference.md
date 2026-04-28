# API Reference

> Back to: [README](../README.md) | [Program Structure](program-structure.md) | [Interfaces](interfaces.md) | [Data Models](data-models.md) | [Modules](modules.md)

## Lambda Functions

### 1. IPAM Delegation Lambda

**Function Name:** `lambda-vpc-ipam-delegate-admin`  
**Source:** `vpc-ipam-delegation.yaml` → `rIpamLambdaDelegate` (inline ZipFile)  
**Duplicate:** `lambda/lambda-vpc-ipam-delegation.py`

#### `lambda_handler(event, context)`

Handles CloudFormation Custom Resource lifecycle events for IPAM delegation.

| Request Type | Action | AWS API Call |
|-------------|--------|-------------|
| Create | Enable IPAM delegation | `ec2.enable_ipam_organization_admin_account(DryRun=False, DelegatedAdminAccountId=<accountid>)` |
| Update | Enable IPAM delegation (same as Create) | `ec2.enable_ipam_organization_admin_account(DryRun=False, DelegatedAdminAccountId=<accountid>)` |
| Delete | Disable IPAM delegation | `ec2.disable_ipam_organization_admin_account(DryRun=False, DelegatedAdminAccountId=<accountid>)` |

**Parameters:**
- `event['ResourceProperties']['accountid']` — The AWS Account ID to delegate/undelegate

**Return:** None (signals via `cfnresponse.send()`)

---

### 2. IPAM Pool Lookup Lambda

**Function Name:** (unnamed — uses CloudFormation auto-generated name)  
**Source:** `custom-vpc.yaml` → `rIpamLambdaGetPoolId` (inline ZipFile)

#### `lambda_handler(event, context)`

Retrieves the IPAM Pool ID matching the current region and environment.

| Request Type | Action | AWS API Call |
|-------------|--------|-------------|
| Create | Query IPAM pools | `ec2.describe_ipam_pools(DryRun=False, Filters=[{'Name': 'locale', 'Values': [region]}])` |
| Update | No-op | None |
| Delete | No-op | None |

**Environment Variables Used:**
- `AWS_REGION` — Filters pools by locale
- `ENVIRONMENT` — Matches against `AllocationResourceTags` values

**Return Data:**
- `responseData['Data']` = IPAM Pool ID (accessed via `!GetAtt rCustomGetPoolId.Data`)

---

## CloudFormation Custom Resources

### `Custom::IPAM`

**Template:** `vpc-ipam-delegation.yaml`  
**Logical ID:** `rIpam`

```yaml
Type: Custom::IPAM
Properties:
  accountid: !Ref pNetworkAccountId
  ServiceToken: !GetAtt rIpamLambdaDelegate.Arn
```

**Lifecycle:** Creates/updates delegation on stack create/update; revokes on stack delete.

### `Custom::GetIpamPoolId`

**Template:** `custom-vpc.yaml`  
**Logical ID:** `rCustomGetPoolId`

```yaml
Type: Custom::GetIpamPoolId
Properties:
  ServiceToken: !GetAtt rIpamLambdaGetPoolId.Arn
```

**Return Attribute:** `!GetAtt rCustomGetPoolId.Data` → IPAM Pool ID string  
**Lifecycle:** Queries pools on create; no-ops on update/delete.

---

## AWS API Calls Used

### EC2 IPAM APIs

| API Call | Lambda | IAM Action |
|----------|--------|------------|
| `enable_ipam_organization_admin_account` | Delegation Lambda | `ec2:EnableIpamOrganizationAdminAccount` |
| `disable_ipam_organization_admin_account` | Delegation Lambda | `ec2:DisableIpamOrganizationAdminAccount` |
| `describe_ipam_pools` | Pool Lookup Lambda | `ec2:DescribeIpamPools` |

### Organizations APIs (IAM permissions, invoked by EC2 service)

| IAM Action | Purpose |
|------------|---------|
| `organizations:RegisterDelegatedAdministrator` | Register Network Account as delegated admin |
| `organizations:DeregisterDelegatedAdministrator` | Deregister on stack delete |
| `organizations:EnableAWSServiceAccess` | Enable IPAM service access in Organizations |

### IAM APIs (IAM permissions, invoked by EC2 service)

| IAM Action | Purpose |
|------------|---------|
| `iam:CreateServiceLinkedRole` | Create IPAM service-linked role |

---

## CloudFormation Declarative Resources

### `vpc-ipam-pools.yaml` Resources

| Resource Type | Count | Key Properties |
|---------------|-------|----------------|
| `AWS::EC2::IPAM` | 1 | OperatingRegions (3 regions configured) |
| `AWS::EC2::IPAMScope` | 1 | IpamScopeType: private |
| `AWS::EC2::IPAMPool` | 9 | Hierarchical: 1 top + 2 regional + 6 environment |
| `AWS::RAM::ResourceShare` | 1 | Shares to Organization, AllowExternalPrincipals: false |

### `custom-vpc.yaml` Resources

| Resource Type | Count | Purpose |
|---------------|-------|---------|
| `AWS::EC2::VPC` | 1 | VPC with IPAM-allocated CIDR |
| `AWS::EC2::Subnet` | 9 | 3 tiers × 3 AZs |
| `AWS::EC2::RouteTable` | 7 | 1 public + 3 hybrid + 3 private |
| `AWS::EC2::Route` | 7 | Default routes |
| `AWS::EC2::SubnetRouteTableAssociation` | 9 | Subnet-to-route table bindings |
| `AWS::EC2::InternetGateway` | 1 | Internet access for public subnets |
| `AWS::EC2::VPCGatewayAttachment` | 1 | IGW-to-VPC attachment |
| `AWS::EC2::NatGateway` | 3 | One per AZ |
| `AWS::EC2::EIP` | 3 | One per NAT Gateway |
| `AWS::Lambda::Function` | 1 | Pool lookup Lambda |
| `AWS::IAM::Role` | 1 | Lambda execution role |
| `AWS::Logs::LogGroup` | 1 | Lambda logs |

---

> See also: [Architecture: Patterns](../architecture/patterns.md) | [Behavior: Workflows](../behavior/workflows.md)
