# OpenShift GitOps Pattern Decision Tree

This document outlines the decision tree for deploying the OpenShift GitOps pattern across different environments.

## Overview

The pattern supports flexible deployment across multiple cluster types, environments, and repository structures. The hierarchy is:

```
Global Defaults
  └── Cluster Set (Home/Work Lab/Cloud)
      └── Topology (SNO/Compact/Full)
          └── Individual Cluster Configuration
```

## Decision Points

### 1. Cluster Set Selection

Choose the environment type that matches your deployment scenario:

#### **Home Lab** (Primary Focus - Fully Supported)

- **Clusters:** Hub (ACM/MCE), Test (dev/test), Prod (production/media)
- **All clusters receive:**
  - External Secrets Operator (Infisical backend)
  - cert-manager (Let's Encrypt)
  - TrueNAS storage
  - Keepalived
  - Goldilocks, VPA, Gatus
  - Generic Device Plugin
  - Node Feature Discovery
  - System Reservation
  - ArgoCD config updates
  - Snapshot finalizer remover
- **Prod cluster adds:** Media ApplicationSet (only enabled apps from values-prod.yaml)
- **Test cluster:** ALL - keepalived - Kasten + MetalLB + Paperless
- **Secrets:** Same Infisical project/environment for all home clusters
- **Certificates:** Let's Encrypt with Cloudflare DNS
- **Values files:** `values-global.yaml` + `values-home.yaml` + `values-{prod|hub|test}.yaml`

#### **Work Lab** (Secondary Focus - Future Support)

- **Clusters:** TBD based on lab setup
- **All clusters receive:** ALL platform components EXCEPT TrueNAS
- **Storage:** ODF or enterprise storage provider
- **Secrets:** Different Infisical project or different secret backend
- **Certificates:** Different certificate provider (internal CA, different ACME provider)
- **Values files:** `values-global.yaml` + `values-worklab.yaml` + `values-{topology}.yaml` + `values-{cluster}.yaml`

#### **Cloud** (Stretch Goal - Future Support)

- **Providers:** ROSA, ARO, IBM Cloud OpenShift (TechZone), Partner Demo
- **Platform components:** Minimal - cloud-managed services preferred
- **Storage:** Cloud-managed (EBS, Azure Disk, IBM Cloud Block)
- **Secrets:** Cloud secret manager (AWS Secrets Manager, Azure Key Vault, IBM Secrets Manager)
- **Certificates:** Cloud certificate manager or Let's Encrypt with cloud DNS provider
- **Values files:** `values-global.yaml` + `values-cloud.yaml` + `values-{provider}.yaml` + `values-{cluster}.yaml`

### 2. Topology Selection

Choose the cluster size that matches your deployment:

#### **Single Node OpenShift (SNO)**

- **Use case:** Edge, small deployments, home lab, dev/test
- **Characteristics:**
  - Single replica (no HA)
  - Smallest deployment size
  - No PodDisruptionBudgets
  - Combined control plane + worker node
- **Resource profile:** Minimal CPU/memory requests
- **Cluster values files:** `values-prod.yaml`, `values-test.yaml` (use roles/sno/)

#### **Compact (3-node)**

- **Use case:** Small production clusters, branch offices
- **Characteristics:**
  - Replica count: 2-3 (allows maintenance without downtime)
  - PDBs configured to allow single node maintenance
  - Smallest deployment size for most apps including OpenShift GitOps
  - Control plane nodes also run workloads
- **Resource profile:** Small CPU/memory requests
- **Values file:** `values-compact.yaml`

#### **Full Cluster (6+ nodes)**

- **Use case:** Production clusters, large deployments
- **Characteristics:**
  - Standard replica count (3+ for HA)
  - Standard PDBs (minAvailable: 2)
  - Standard deployment sizes
  - Dedicated control plane nodes (3) + worker nodes (3+)
- **Resource profile:** Standard CPU/memory requests
- **Values file:** `values-full.yaml`

### 3. Repository Structure Selection

Choose how to organize your GitOps repositories:

#### **Mono Repo** (Current - Fully Supported)

- **Structure:** Single repository contains platform + all applications
- **Path:** `rbales79/argo-apps`
- **Layout:**
  ```
  argo-apps/
  ├── charts/
  │   ├── platform/       # 22 platform components
  │   ├── topology/       # Topology-specific configs
  │   └── applications/   # All application charts
  ├── values-*.yaml       # Configuration files
  └── roles/              # Cluster-specific ApplicationSets
  ```
- **Pros:** Simplified management, single source of truth, easier local development
- **Cons:** Larger repo size, all changes in one place

#### **Platform + Apps Repo** (Future)

- **Structure:** Separate repositories for platform and applications
- **Repos:**
  - `platform-gitops/` - Platform components only
  - `apps-gitops/` - All application domains
- **Pros:** Separate RBAC, independent versioning
- **Cons:** More repos to manage

#### **Platform + Per-Domain Apps Repos** (Future)

- **Structure:** Platform repo + one repo per application domain
- **Repos:**
  - `platform-gitops/` - Platform components
  - `ai-apps/` - AI/ML applications
  - `media-apps/` - Media management applications
  - `home-automation-apps/` - IoT/smart home applications
  - etc.
- **Pros:** Fine-grained access control per domain, smaller repos
- **Cons:** Many repos to manage

#### **Platform + Per-App Repos** (Future)

- **Structure:** Platform repo + one repo per application
- **Repos:**
  - `platform-gitops/` - Platform components
  - `litellm/`, `plex/`, `home-assistant/`, etc.
- **Pros:** Maximum isolation, independent app lifecycle
- **Cons:** Repository sprawl, complex management

### 4. Deployment Method Selection

Choose how to deploy the pattern:

#### **Direct to Cluster** (Bootstrap)

- **Use case:** Initial cluster setup, single cluster deployments
- **Method:** ArgoCD Application pointing to cluster role
- **Process:**
  1. Install OpenShift GitOps operator
  2. Create bootstrap Application: `bootstrap/README.md`
  3. ArgoCD deploys all ApplicationSets
  4. ApplicationSets create Applications for platform + apps
- **Values:** Uses cluster-specific values file

#### **ACM/MCE Deployment** (Multi-cluster)

- **Use case:** Managing multiple clusters from hub
- **Method:** ACM ApplicationSet or Policy deploying ArgoCD Applications
- **Process:**
  1. Hub cluster has ACM/MCE installed
  2. Create ACM ApplicationSet targeting managed clusters
  3. ACM deploys ArgoCD Applications to each cluster
  4. ArgoCD on each cluster deploys platform + apps
- **Values:** Can target different cluster sets/topologies
- **Supports:**
  - Platform only (deploy platform components to all clusters)
  - Apps only (deploy applications to specific clusters)
  - Both (full stack deployment)

#### **Platform Only Deployment**

- **Scenario:** Deploy only platform components (ESO, cert-manager, storage, etc.)
- **Use case:** Prepare clusters before app deployment
- **Method:** Target only platform ApplicationSets
- **Values:** Set all `applicationStacks.*.enabled: false`

#### **Apps Only Deployment**

- **Scenario:** Deploy only applications (assume platform already exists)
- **Use case:** Application-focused deployment on pre-configured clusters
- **Method:** Target only application ApplicationSets
- **Values:** Set all `platformComponents.*.enabled: false`

### 5. Certificate Provider Configuration

Certificates are configurable per cluster set and cluster:

#### **Home Lab - Let's Encrypt + Cloudflare DNS**

```yaml
certificates:
  provider: letsencrypt
  letsencrypt:
    issuer: production
    email: rbales79@gmail.com
    server: https://acme-v02.api.letsencrypt.org/directory
    dns:
      provider: cloudflare
      apiTokenSecretRef: cloudflare-api-token
```

#### **Work Lab - Internal CA or Different ACME**

```yaml
certificates:
  provider: internal-ca # or "letsencrypt-route53"
  internalCA:
    issuerRef: corporate-ca
    duration: 2160h # 90 days
  # OR
  letsencrypt:
    issuer: staging # or production
    dns:
      provider: route53 # AWS Route53 for DNS validation
      region: us-east-1
```

#### **Cloud - Cloud Certificate Manager**

```yaml
certificates:
  provider: aws-acm # or azure-keyvault, ibm-secrets-manager
  aws:
    region: us-east-1
    certificateArn: arn:aws:acm:...
  # OR Let's Encrypt with cloud DNS
  letsencrypt:
    issuer: production
    dns:
      provider: route53 # or azure-dns, ibm-cloud-dns
```

### 6. External Secrets Provider Configuration

Secrets are configurable per cluster set:

#### **Home Lab - Infisical**

```yaml
externalSecrets:
  provider: infisical
  secret: infisical-auth-secret
  infisical:
    projectSlug: hub
    environmentSlug: prod
    apiUrl: https://app.infisical.com
```

#### **Work Lab - Different Infisical Project or Vault**

```yaml
externalSecrets:
  provider: infisical # or vault
  secret: worklab-secrets
  infisical:
    projectSlug: worklab
    environmentSlug: prod
  # OR
  vault:
    server: https://vault.corporate.com
    namespace: engineering
    authPath: kubernetes
```

#### **Cloud - Cloud Secret Manager**

```yaml
externalSecrets:
  provider: aws-secrets-manager # or azure-keyvault, ibm-secrets-manager
  aws:
    region: us-east-1
    roleArn: arn:aws:iam::...
  # OR
  azure:
    vaultUrl: https://myvault.vault.azure.net
    tenantId: ...
```

### 7. Multi-Hub Architecture

Supports multiple hub clusters for blast radius reduction:

#### **Same Datacenter - Multiple Hubs**

```
Hub1 (hub1.roybales.com)
  ├── sno (production-1)
  ├── test (dev-1)
  └── compact-1

Hub2 (hub2.roybales.com)
  ├── sno (production-2)
  ├── compact-2
  └── full-1
```

**Configuration:**

- Each hub has ACM/MCE enabled: `platformComponents.acm.enabled: true`
- Managed clusters target specific hub via `managedClusters` in hub values
- Shared Infisical project or separate projects per hub
- Same certificate provider across all hubs

#### **Different Datacenters - Geographic Distribution**

```
Hub1 - East Coast (hub-east.roybales.com)
  ├── cluster1-east
  ├── cluster2-east
  └── cluster3-east

Hub2 - West Coast (hub-west.roybales.com)
  ├── cluster1-west
  ├── cluster2-west
  └── cluster3-west
```

**Configuration:**

- Region-specific values files: `values-region-east.yaml`, `values-region-west.yaml`
- Potentially different certificate providers (regional CAs)
- Regional secret backends or separate Infisical environments
- Geographic load balancing considerations

## Values File Hierarchy

The complete hierarchy for a cluster deployment:

```bash
# Example: Production cluster in home lab (SNO topology)
helm install prod ./roles/sno \
  -f values-global.yaml \           # Global defaults
  -f clusters/sets/values-home.yaml \              # Home cluster set
  -f clusters/individual-clusters/values-prod.yaml                # Production cluster config

# Example: Compact cluster in work lab
helm install compact1 ./roles/compact \
  -f values-global.yaml \
  -f clusters/sets/values-worklab.yaml \
  -f clusters/topologies/values-compact.yaml \
  -f values-compact1.yaml

# Example: Full cluster in AWS (ROSA)
helm install prod-rosa ./roles/full \
  -f values-global.yaml \
  -f clusters/sets/values-cloud.yaml \
  -f clusters/sets/values-cloud-rosa.yaml \
  -f clusters/topologies/values-full.yaml \
  -f clusters/individual-clusters/values-prod-rosa.yaml
```

## Application-Specific Configuration

Applications may need additional configuration per cluster or namespace:

### Cluster-Level App Configuration

```yaml
# In cluster values file
applicationStacks:
  media:
    enabled: true
    plex:
      # Cluster-specific overrides
      loadBalancerIP: 192.168.1.200
      storage:
        size: 500Gi
    sonarr:
      loadBalancerIP: 192.168.1.201
```

### Namespace-Level App Configuration

```yaml
# In cluster values file
applications:
  plex:
    namespace: plex
    labels:
      environment: production
      backup: "true"
    config:
      # App-specific configuration
      transcoding:
        enabled: true
        gpu: amd
```

## Current Status

| Feature              | Status       | Notes                                 |
| -------------------- | ------------ | ------------------------------------- |
| Home Lab             | ✅ Supported | Primary focus, fully implemented      |
| SNO Topology         | ✅ Supported | Tested on home clusters               |
| Compact Topology     | 🔄 Partial   | Values files created, needs testing   |
| Full Topology        | 🔄 Partial   | Values files created, needs testing   |
| Mono Repo            | ✅ Supported | Current repository structure          |
| Work Lab             | ⏳ Planned   | Secondary focus                       |
| Cloud (ROSA/ARO/IBM) | ⏳ Future    | Stretch goal                          |
| Multi-repo           | ⏳ Future    | Not yet implemented                   |
| ACM Deployment       | 🔄 Partial   | ACM installed, ApplicationSets needed |
| Direct Deployment    | ✅ Supported | Bootstrap process documented          |
| Let's Encrypt        | ✅ Supported | With Cloudflare DNS                   |
| Internal CA          | ⏳ Planned   | For work lab                          |
| Cloud Certs          | ⏳ Future    | AWS ACM, Azure Key Vault, etc.        |
| Infisical Secrets    | ✅ Supported | Current backend                       |
| Vault Secrets        | ⏳ Planned   | For work lab                          |
| Cloud Secrets        | ⏳ Future    | AWS/Azure/IBM secret managers         |

## Next Steps

1. ✅ Create cluster set values files (home, worklab, cloud)
2. 🔄 Create ApplicationSets for platform layer
3. ⏳ Create ApplicationSets for application layers
4. ⏳ Test on home lab clusters
5. ⏳ Document ACM deployment process
6. ⏳ Add work lab certificate provider support
7. ⏳ Add work lab storage provider support
8. ⏳ Test compact topology
9. ⏳ Test full topology
10. ⏳ Add cloud provider support
