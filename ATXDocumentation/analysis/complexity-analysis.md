# Complexity Analysis

> Back to: [README](../README.md) | [Code Metrics](code-metrics.md) | [Dependency Analysis](dependency-analysis.md) | [Security Patterns](security-patterns.md) | [Tech Debt](tech-debt.md)

## Lambda Function Complexity

### IPAM Delegation Lambda — Low Complexity

**Cyclomatic Complexity:** 5

Decision points:
1. `if RequestType == 'Create' or RequestType == 'Update'`
2. `if response['Success'] == True` (Create/Update path)
3. `except ClientError` (Create/Update path)
4. `elif RequestType == 'Delete'`
5. `if response['Success'] == True` (Delete path)
6. `except ClientError` (Delete path)

**Lines of executable code:** ~30  
**Nesting depth:** 3 (function → if/elif → try/except)  
**Assessment:** Simple, linear control flow with symmetric Create/Delete handling.

### IPAM Pool Lookup Lambda — Medium Complexity

**Cyclomatic Complexity:** 8

Decision points:
1. `if event['RequestType'] == 'Create'`
2. `if len(ipam_pool['IpamPools']) == 0`
3. `for ip_pool in ipam_pool['IpamPools']` (loop)
4. `if ip_pool['AllocationResourceTags']` (truthy check)
5. `for tag in ip_pool['AllocationResourceTags']` (nested loop)
6. `if tag['Value'] == environment`
7. `elif len(ip_pool['AllocationResourceTags']) == 0`
8. `except ClientError`

**Lines of executable code:** ~35  
**Nesting depth:** 5 (function → if → try → for → for → if)  
**Assessment:** Moderate complexity with nested loops and multiple conditional branches. The double-loop pattern (pools × tags) increases cognitive complexity.

## CloudFormation Template Complexity

### `vpc-ipam-delegation.yaml` — Low Complexity

| Metric | Value |
|--------|-------|
| Parameters | 3 |
| Resources | 4 |
| Mappings | 0 |
| Conditions | 0 |
| Outputs | 0 |
| Intrinsic functions | ~15 |
| Lines | 131 |
| Custom Resources | 1 |

**Assessment:** Straightforward template with minimal resources and no conditional logic.

### `vpc-ipam-pools.yaml` — Medium Complexity

| Metric | Value |
|--------|-------|
| Parameters | 8 |
| Resources | 12 |
| Mappings | 0 |
| Conditions | 0 |
| Outputs | 0 |
| Intrinsic functions | ~35 |
| Lines | 265 |
| Custom Resources | 0 |

**Assessment:** Moderate complexity due to repetitive pool definitions. The hierarchical pool structure (9 pools in 3 tiers) is structurally complex but each pool definition follows the same pattern. Heavy use of `!Select` with list parameters adds reference complexity.

### `custom-vpc.yaml` — High Complexity

| Metric | Value |
|--------|-------|
| Parameters | 3 (+2 in metadata only) |
| Resources | 45 |
| Mappings | 1 (3 size tiers) |
| Conditions | 0 |
| Outputs | 0 |
| Intrinsic functions | ~80+ |
| Lines | 449 |
| Custom Resources | 1 |

**Assessment:** Most complex template. 45 resources with heavy use of `Fn::Cidr`, `FindInMap`, `Select`, and `GetAZs` for dynamic subnet calculation. The 9 subnets × (route tables + routes + associations) pattern creates significant repetition.

## IPAM Pool Hierarchy Nesting Depth

```
Level 0: IPAM Instance (rIpam)
  └── Level 1: IPAM Scope (rIpamScope)
        └── Level 2: Top Pool (rIpamTopPoolIpv4)
              ├── Level 3: Regional Pool 1 (rIpamPoolRegional1Ipv4)
              │     ├── Level 4: Prod Pool (rIpamPoolRegional1ProdIpv4)
              │     ├── Level 4: UAT Pool (rIpamPoolRegional1UatIpv4)
              │     └── Level 4: Dev Pool (rIpamPoolRegional1DevIpv4)
              └── Level 3: Regional Pool 2 (rIpamPoolRegional2Ipv4)
                    ├── Level 4: Prod Pool (rIpamPoolRegional2ProdIpv4)
                    ├── Level 4: UAT Pool (rIpamPoolRegional2UatIpv4)
                    └── Level 4: Dev Pool (rIpamPoolRegional2DevIpv4)
```

**Maximum nesting depth:** 4 levels (IPAM → Scope → Top Pool → Regional → Environment)  
**Total nodes:** 13 (1 IPAM + 1 Scope + 1 Top Pool + 2 Regional + 6 Environment + 1 RAM Share + 1 unreferenced Region 3 in RAM)

## Overall Complexity Assessment

| Component | Structural Complexity | Cognitive Complexity | Maintenance Risk |
|-----------|-----------------------|---------------------|------------------|
| Delegation template | Low | Low | Low |
| Delegation Lambda | Low | Low | Low |
| Pools template | Medium | Medium | Medium (repetitive patterns) |
| VPC template | High | Medium | Medium (repetitive patterns) |
| Pool Lookup Lambda | Medium | Medium | Medium (nested loops) |
| Cross-template dependencies | Medium | High | High (implicit ordering) |

---

> See also: [Code Metrics](code-metrics.md) | [Architecture: Patterns](../architecture/patterns.md)
