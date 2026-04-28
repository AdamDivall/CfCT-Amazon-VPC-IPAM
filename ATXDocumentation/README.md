# CfCT Amazon VPC IPAM — Documentation Hub

## Quick Navigation

| Section | Description |
|---------|-------------|
| 📋 [Project Overview](project-overview.md) | Purpose, technology stack, architecture summary |
| 🔴 [Technical Debt Report](technical-debt-report.md) | **AWS Transformation Recommendation** + prioritized findings |

---

## 📐 Architecture

| Document | Description |
|----------|-------------|
| [System Overview](architecture/system-overview.md) | High-level architecture, technology stack, deployment model |
| [Components](architecture/components.md) | Three major components: Delegation, Pools, VPC |
| [Dependencies](architecture/dependencies.md) | Deployment order, external services, cross-template data flow |
| [Patterns](architecture/patterns.md) | Custom Resources, Delegated Admin, hierarchical pools, CfCT |

## 🔄 Behavior *(Early Access)*

| Document | Description |
|----------|-------------|
| [Business Logic](behavior/business-logic.md) | IPAM delegation, pool lookup, VPC CIDR allocation, subnet calculation |
| [Workflows](behavior/workflows.md) | Delegation, pool setup, and VPC provisioning workflows |
| [Decision Logic](behavior/decision-logic.md) | All decision points in Lambda functions and templates |
| [Error Handling](behavior/error-handling.md) | Exception handling, cfnresponse signaling, gap analysis |

## 📊 Analysis

| Document | Description |
|----------|-------------|
| [Code Metrics](analysis/code-metrics.md) | File counts, LOC, resource counts, Lambda metrics |
| [Complexity Analysis](analysis/complexity-analysis.md) | Cyclomatic complexity, template complexity, pool hierarchy depth |
| [Dependency Analysis](analysis/dependency-analysis.md) | Internal/external dependencies, cross-template data flow |
| [Security Patterns](analysis/security-patterns.md) | IAM analysis, parameter validation, RAM security, encryption |
| [Tech Debt](analysis/tech-debt.md) | Consolidated technical debt assessment with severity ratings |

## 📚 Reference

| Document | Description |
|----------|-------------|
| [Program Structure](reference/program-structure.md) | Complete file listing with descriptions and statistics |
| [Interfaces](reference/interfaces.md) | Lambda handler interfaces, CloudFormation parameter interfaces |
| [Data Models](reference/data-models.md) | Parameter types, VPC size mappings, pool hierarchy model |
| [API Reference](reference/api-reference.md) | Lambda functions, Custom Resources, AWS API calls |
| [Modules](reference/modules.md) | Module organization and cross-module data flow |

## 🔴 Technical Debt

| Document | Description |
|----------|-------------|
| [Technical Debt Report](technical-debt-report.md) | Root-level executive summary with AWS recommendation |
| [Summary](technical-debt/summary.md) | Overview of all technical debt findings |
| [Outdated Components](technical-debt/outdated-components.md) | Python 3.9 EOL analysis, dependency assessment |
| [Maintenance Burden](technical-debt/maintenance-burden.md) | Duplicate code, hardcoded regions, resource reference bugs |
| [Remediation Plan](technical-debt/remediation-plan.md) | Prioritized action items with specific upgrade paths |

## 📊 Diagrams

| Document | Description |
|----------|-------------|
| [Structural Diagrams](diagrams/structural/component-diagrams.md) | Component, pool hierarchy, and VPC network diagrams |
| [Behavioral Diagrams](diagrams/behavioral/sequence-diagrams.md) | Sequence diagrams for delegation and VPC provisioning |
| [Architecture Diagrams](diagrams/architecture/system-context.md) | System context, integration patterns, security boundaries |

## 🚀 Migration

| Document | Description |
|----------|-------------|
| [Component Order](migration/component-order.md) | Deployment sequence and dependency matrix |
| [Test Specifications](migration/test-specifications.md) | Test cases for template validation and Lambda behavior |
| [Validation Criteria](migration/validation-criteria.md) | Success criteria for each component deployment |

## 🔧 Specialized

| Document | Description |
|----------|-------------|
| [Infrastructure Patterns](specialized/infrastructure-patterns.md) | CfCT manifest config, ZipFile Lambda, Fn::Cidr patterns |

---

## Project Summary

**CfCT Amazon VPC IPAM** is an IaC solution for managing Amazon VPC IP Address Manager across a multi-account AWS environment using Customizations for Control Tower. It consists of 3 CloudFormation templates and supporting files (~925 LOC) that automate IPAM delegation, hierarchical pool creation, and VPC provisioning with automatic CIDR allocation.

**Key Technical Debt:** Python 3.9 runtime approaching EOL — recommended transformation: `AWS/python-version-upgrade`.
