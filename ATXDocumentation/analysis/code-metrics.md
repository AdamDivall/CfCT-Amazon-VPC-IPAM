# Code Metrics

> Back to: [README](../README.md) | [Complexity Analysis](complexity-analysis.md) | [Dependency Analysis](dependency-analysis.md) | [Security Patterns](security-patterns.md) | [Tech Debt](tech-debt.md)

## File Inventory

| File | Type | Lines | Size Role |
|------|------|-------|-----------|
| `lambda/lambda-vpc-ipam-delegation.py` | Python | 34 | Lambda handler (unused duplicate) |
| `vpc-ipam-delegation.yaml` | CloudFormation | 131 | IPAM delegation template |
| `vpc-ipam-delegation.json` | JSON | 13 | CfCT parameter file |
| `vpc-ipam-pools.yaml` | CloudFormation | 265 | IPAM pools template |
| `vpc-ipam-pools.json` | JSON | 33 | CfCT parameter file |
| `custom-vpc.yaml` | CloudFormation | 449 | VPC provisioning template |
| `readme.md` | Markdown | 116 | Project documentation |
| **Total** | | **1,041** | |

## Lines of Code by Category

| Category | Files | Lines | % of Total |
|----------|-------|-------|------------|
| CloudFormation Templates | 3 | 845 | 81.2% |
| Documentation | 1 | 116 | 11.1% |
| JSON Parameters | 2 | 46 | 4.4% |
| Python | 1 | 34 | 3.3% |

## CloudFormation Resource Counts

### `vpc-ipam-delegation.yaml` — 4 Resources

| Resource Type | Count |
|---------------|-------|
| `AWS::Logs::LogGroup` | 1 |
| `AWS::IAM::Role` | 1 |
| `AWS::Lambda::Function` | 1 |
| `Custom::IPAM` | 1 |

### `vpc-ipam-pools.yaml` — 12 Resources

| Resource Type | Count |
|---------------|-------|
| `AWS::EC2::IPAM` | 1 |
| `AWS::EC2::IPAMScope` | 1 |
| `AWS::EC2::IPAMPool` | 9 |
| `AWS::RAM::ResourceShare` | 1 |

### `custom-vpc.yaml` — 45 Resources

| Resource Type | Count |
|---------------|-------|
| `AWS::Logs::LogGroup` | 1 |
| `AWS::IAM::Role` | 1 |
| `AWS::Lambda::Function` | 1 |
| `Custom::GetIpamPoolId` | 1 |
| `AWS::EC2::VPC` | 1 |
| `AWS::EC2::InternetGateway` | 1 |
| `AWS::EC2::VPCGatewayAttachment` | 1 |
| `AWS::EC2::Subnet` | 9 |
| `AWS::EC2::RouteTable` | 7 |
| `AWS::EC2::Route` | 7 |
| `AWS::EC2::SubnetRouteTableAssociation` | 9 |
| `AWS::EC2::EIP` | 3 |
| `AWS::EC2::NatGateway` | 3 |

**Total Resources Across All Templates: 61**

## Lambda Function Metrics

| Property | Delegation Lambda | Pool Lookup Lambda |
|----------|------------------|--------------------|
| Template | `vpc-ipam-delegation.yaml` | `custom-vpc.yaml` |
| Resource ID | `rIpamLambdaDelegate` | `rIpamLambdaGetPoolId` |
| Runtime | python3.9 | python3.9 |
| Memory | 128 MB | 128 MB |
| Timeout | 60 seconds | 60 seconds |
| Handler | `index.lambda_handler` | `index.lambda_handler` |
| Code Type | Inline ZipFile | Inline ZipFile |
| Code Lines | ~30 | ~35 |
| Environment Vars | None | `ENVIRONMENT` |
| Named | `lambda-vpc-ipam-delegate-admin` | Auto-generated |

## Parameter Counts

| Template | Parameters | With Validation | With Defaults |
|----------|-----------|-----------------|---------------|
| `vpc-ipam-delegation.yaml` | 3 | 3 | 1 |
| `vpc-ipam-pools.yaml` | 8 | 3 | 0 |
| `custom-vpc.yaml` | 3 | 3 | 2 |
| **Total** | **14** | **9** | **3** |

## CloudFormation Intrinsic Functions Used

| Function | Usage Count (approx.) | Templates |
|----------|-----------------------|-----------|
| `!Ref` | 40+ | All |
| `!GetAtt` | 20+ | delegation, custom-vpc |
| `!Sub` | 3 | delegation, custom-vpc, pools |
| `!Select` | 25+ | pools, custom-vpc |
| `!Cidr` | 9 | custom-vpc |
| `!FindInMap` | 9 | custom-vpc |
| `!GetAZs` | 9 | custom-vpc |

---

> See also: [Complexity Analysis](complexity-analysis.md) | [Reference: Program Structure](../reference/program-structure.md)
