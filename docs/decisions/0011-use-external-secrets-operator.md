---
status: accepted
date: 2025-11-08
decision-makers: ["Platform Engineering Team"]
---

# Use External Secrets Operator for Secret Management

## Context and Problem Statement

Applications require sensitive configuration data (API keys, passwords, certificates) that should not be stored in Git. The platform needs a secure, GitOps-compatible method for managing secrets across multiple clusters with different secret backends (Infisical for home lab, native Kubernetes secrets for testing).

## Decision Drivers

- **GitOps Compatibility:** Secret management must work with declarative GitOps workflows
- **Multi-Backend Support:** Different environments use different secret stores (Infisical, AWS Secrets Manager, HashiCorp Vault)
- **Kubernetes-Native:** Should integrate naturally with Kubernetes/OpenShift
- **Declarative Configuration:** Secret definitions should be code (ExternalSecret CRs)
- **Multi-Cluster:** Same pattern must work across hub, prod, and test clusters
- **Operator Support:** OpenShift's operator ecosystem provides pre-packaged solutions

## Considered Options

1. **External Secrets Operator (ESO)** - Kubernetes operator that syncs secrets from external backends
2. **Sealed Secrets** - Encrypted secrets stored in Git
3. **HashiCorp Vault Injector** - Sidecar injection pattern
4. **Native Kubernetes Secrets** - Manual secret creation per cluster
5. **Argo CD Vault Plugin** - Argo CD native secret handling

## Decision Outcome

Chosen option: **External Secrets Operator (ESO)**, because:

- **Multi-backend flexibility:** Supports Infisical, AWS, Azure, GCP, Vault, and more
- **GitOps-native:** ExternalSecret CRs are stored in Git, actual secrets are synced
- **OpenShift support:** Available as certified operator
- **Declarative:** Applications reference ExternalSecrets, operator handles sync
- **Separation of concerns:** Secret backend config separate from application config
- **Active development:** Well-maintained CNCF project

### Consequences

#### Good

- Applications can reference secrets declaratively via ExternalSecret CRs
- Secret backends can differ per cluster (Infisical in home lab, AWS in cloud)
- No sensitive data in Git repository
- Automatic secret rotation when backend values change
- Supports multiple secret stores simultaneously
- ClusterSecretStore pattern allows cluster-wide secret backend configuration

#### Bad

- Additional operator to manage (overhead, updates)
- Applications depend on ESO being healthy (sync-wave 0 mitigates this)
- Secret backend outage affects secret sync (cached secrets mitigate this)
- Learning curve for ExternalSecret CR syntax

#### Neutral

- Requires secret backend infrastructure (Infisical, Vault, cloud provider)
- ExternalSecret CRs must be created per application
- ClusterSecretStore must be configured per cluster

## Implementation

### Platform Component

ESO deployed as core platform component in `charts/platform/external-secrets-operator/`:

- Sync wave 0 (deployed before applications)
- ClusterSecretStore configured per environment
- RBAC for secret access

### Application Pattern

Applications reference secrets via ExternalSecret CRs:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: cluster-secret-store
    kind: ClusterSecretStore
  target:
    name: app-secrets
  data:
    - secretKey: api-key
      remoteRef:
        key: /apps/myapp/api-key
```

### Cluster Configuration

Different backends per environment:

- **Home lab:** Infisical (self-hosted)
- **Work lab:** Infisical (different instance)
- **Cloud:** AWS Secrets Manager / Azure Key Vault

## Links

- **Official Docs:** https://external-secrets.io/
- **Operator Hub:** https://operatorhub.io/operator/external-secrets-operator
- **Implementation:** `charts/platform/external-secrets-operator/`
- **Configuration Guide:** `docs/CONFIGURATION-GUIDE.md`
- **Related ADRs:**
  - [ADR-002: Validated Patterns Framework](0002-validated-patterns-framework-migration.md) - Platform layer
  - [ADR-006: Chart Standards](0006-chart-standards-and-security.md) - Security patterns
