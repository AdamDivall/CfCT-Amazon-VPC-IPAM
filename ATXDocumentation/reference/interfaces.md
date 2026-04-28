# Interfaces

> Back to: [README](../README.md) | [Program Structure](program-structure.md) | [Data Models](data-models.md) | [API Reference](api-reference.md) | [Modules](modules.md)

## Lambda Function Interfaces

### 1. IPAM Delegation Lambda (`rIpamLambdaDelegate`)

**Source:** `vpc-ipam-delegation.yaml` (inline ZipFile), `lambda/lambda-vpc-ipam-delegation.py` (standalone)

```python
def lambda_handler(event: dict, context: LambdaContext) -> None
```

**Input Event (CloudFormation Custom Resource):**
```json
{
  "RequestType": "Create" | "Update" | "Delete",
  "ResourceProperties": {
    "accountid": "<12-digit AWS Account ID>",
    "ServiceToken": "<Lambda ARN>"
  },
  "StackId": "<CloudFormation Stack ARN>",
  "RequestId": "<Unique Request ID>",
  "LogicalResourceId": "rIpam",
  "ResponseURL": "<Pre-signed S3 URL>"
}
```

**Output:** None (sends response via `cfnresponse.send()`)

**Response Signals:**
- `cfnresponse.SUCCESS` — API call succeeded
- `cfnresponse.FAILED` — `ClientError` exception caught

### 2. IPAM Pool Lookup Lambda (`rIpamLambdaGetPoolId`)

**Source:** `custom-vpc.yaml` (inline ZipFile)

```python
def lambda_handler(event: dict, context: LambdaContext) -> None
```

**Input Event (CloudFormation Custom Resource):**
```json
{
  "RequestType": "Create" | "Update" | "Delete",
  "ResourceProperties": {
    "ServiceToken": "<Lambda ARN>"
  },
  "StackId": "<CloudFormation Stack ARN>",
  "RequestId": "<Unique Request ID>",
  "LogicalResourceId": "rCustomGetPoolId",
  "ResponseURL": "<Pre-signed S3 URL>"
}
```

**Environment Variables:**
| Variable | Source | Description |
|----------|--------|-------------|
| `ENVIRONMENT` | `pTagEnvironment` parameter | Environment name to match against IPAM pool AllocationResourceTags |
| `AWS_REGION` | Lambda runtime (automatic) | Current region for IPAM pool locale filtering |

**Output Response Data:**
```json
{
  "Data": "<IPAM Pool ID>"
}
```

**Response Signals:**
- `cfnresponse.SUCCESS` — Matching pool found
- `cfnresponse.FAILED` — No matching pool or API error

## CloudFormation Parameter Interfaces

### `vpc-ipam-delegation.yaml` Parameters

| Parameter | Type | Constraints | Required |
|-----------|------|-------------|----------|
| `pNetworkAccountId` | String | `AllowedPattern: ^[0-9]{12}$`, Min/MaxLength: 12 | Yes |
| `pLambdaLogGroupRetention` | String | `AllowedValues: [1,3,5,7,14,30,60,90,120,150,180,365,400,545,731,1827,3653]`, Default: 365 | No |
| `pTagEnvironment` | String | `AllowedValues: [Production, UAT, Development]` | Yes |

### `vpc-ipam-pools.yaml` Parameters

| Parameter | Type | Constraints | Required |
|-----------|------|-------------|----------|
| `pOrganizationId` | String | `AllowedPattern: ^[o][\-][a-z0-9]{10}$`, Min/MaxLength: 12 | Yes |
| `pManagementAccountId` | String | `AllowedPattern: ^[0-9]{12}$`, Min/MaxLength: 12 | Yes |
| `pOperatingRegionList` | List\<String\> | None | Yes |
| `pMainPoolCidrIpv4List` | List\<String\> | None | Yes |
| `pProdPoolCidrIpv4List` | List\<String\> | None | Yes |
| `pUatPoolCidrIpv4List` | List\<String\> | None | Yes |
| `pDevPoolCidrIpv4List` | List\<String\> | None | Yes |
| `pTagEnvironment` | String | `AllowedValues: [Production, UAT, Development]` | Yes |

### `custom-vpc.yaml` Parameters

| Parameter | Type | Constraints | Required |
|-----------|------|-------------|----------|
| `pLambdaLogGroupRetention` | String | `AllowedValues: [1,3,5,...,3653]`, Default: 365 | No |
| `pVpcSize` | String | `AllowedValues: [Small, Medium, Large]`, Default: Small | No |
| `pTagEnvironment` | String | `AllowedValues: [Production, Development]` ⚠️ Missing UAT | Yes |

## CloudFormation Custom Resource Interfaces

### `Custom::IPAM` (Delegation)
```yaml
Type: Custom::IPAM
Properties:
  accountid: !Ref pNetworkAccountId   # 12-digit AWS Account ID
  ServiceToken: !GetAtt rIpamLambdaDelegate.Arn
```

### `Custom::GetIpamPoolId` (Pool Lookup)
```yaml
Type: Custom::GetIpamPoolId
Properties:
  ServiceToken: !GetAtt rIpamLambdaGetPoolId.Arn
```
**Return Attribute:** `!GetAtt rCustomGetPoolId.Data` → IPAM Pool ID string

---

> See also: [API Reference](api-reference.md) | [Behavior: Business Logic](../behavior/business-logic.md)
