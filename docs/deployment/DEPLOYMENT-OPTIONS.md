# Deployment Options

Choose the right deployment pattern for your use case. This guide helps you select and implement the best approach for your infrastructure needs.

> **📋 Related Documentation:** See also [ADR 008: Multi-Cluster Management Strategy](../decisions/008-multi-cluster-management-strategy.md) for the architectural rationale.

## 🎯 Decision Tree

```
Start Here
    │
    ├─ Single cluster for testing/learning?
    │   └─ → [Single Cluster Quick Start](#single-cluster-quick-start)
    │
    ├─ Few clusters (2-5), simple management?
    │   └─ → [Multi-Cluster without ACM](#multi-cluster-without-acm)
    │
    ├─ Many clusters (6+), centralized control?
    │   └─ → [Multi-Cluster with ACM](#multi-cluster-with-acm)
    │
    └─ Multiple sites, DR requirements, geographic distribution?
        └─ → [Multi-Site with ACM](#multi-site-multi-cluster-with-acm)
```

---

## 🚀 Deployment Patterns

### Single Cluster Quick Start

**Best for:**

- Learning the framework
- Testing new applications
- Development environments
- Single production environment
- Simple workload deployments

**Infrastructure:**

- 1 OpenShift cluster (SNO, Compact, or Full topology)
- Git repository for GitOps
- Optional: External secrets provider

**Time to Deploy:** ~30 minutes

**Documentation:** [Single Cluster Quick Start](./single-cluster-quickstart.md)

**Pros:**

- ✅ Simplest to set up
- ✅ Minimal infrastructure required
- ✅ Fast to deploy
- ✅ Easy to understand
- ✅ Low operational overhead

**Cons:**

- ❌ Manual replication for multiple clusters
- ❌ No centralized management
- ❌ Per-cluster GitOps state

---

### Multi-Cluster without ACM

**Best for:**

- Small cluster fleets (2-5 clusters)
- Independent cluster management
- Different environments (dev, test, prod)
- Simple multi-cluster scenarios
- Teams comfortable with per-cluster configuration

**Infrastructure:**

- 2-5 OpenShift clusters
- Git repository with cluster-specific values
- Cluster context switching tooling
- Optional: External secrets provider

**Time to Deploy:** ~1 hour per cluster

**Documentation:** [Multi-Cluster Quick Start](./multi-cluster-quickstart.md)

**Pros:**

- ✅ Independent cluster control
- ✅ Cluster-specific configurations
- ✅ No additional management overhead
- ✅ Simple to understand
- ✅ Direct cluster access

**Cons:**

- ❌ Manual cluster provisioning
- ❌ Repetitive configuration
- ❌ No fleet-wide policies
- ❌ Manual cluster switching

---

### Multi-Cluster with ACM

**Best for:**

- Large cluster fleets (6+ clusters)
- Centralized cluster management
- Policy-driven compliance
- Fleet-wide application deployment
- Simplified operational model

**Infrastructure:**

- 1 Hub cluster (management)
- 1+ Managed clusters (workload)
- Advanced Cluster Management (ACM) installed
- Git repository with hub/managed configurations
- Optional: External secrets provider

**Time to Deploy:** ~2 hours (hub setup) + ~30 minutes per managed cluster

**Documentation:** [ACM Quick Start](./acm-quickstart.md)

**Pros:**

- ✅ Centralized management
- ✅ Automated cluster provisioning
- ✅ Policy-based governance
- ✅ Fleet-wide application deployment
- ✅ Single pane of glass
- ✅ Cluster lifecycle automation

**Cons:**

- ❌ Additional hub cluster required
- ❌ More complex architecture
- ❌ Learning curve for ACM concepts
- ❌ Hub cluster is single point of control

---

### Multi-Site, Multi-Cluster with ACM

**Best for:**

- Geographic distribution
- Disaster recovery requirements
- High availability across regions
- Global application deployment
- Compliance with data residency

**Infrastructure:**

- 2+ Hub clusters (per site/region)
- Multiple managed clusters per site
- ACM with multi-hub configuration
- Git repository with site-specific configurations
- Global load balancing (optional)
- Cross-site networking

**Time to Deploy:** ~4 hours per site + ~30 minutes per managed cluster

**Documentation:** [Multi-Site Quick Start](./multi-site-quickstart.md)

**Pros:**

- ✅ Geographic redundancy
- ✅ Disaster recovery capability
- ✅ Regional compliance
- ✅ Reduced latency for users
- ✅ Site-independent operation
- ✅ Scalable to global deployment

**Cons:**

- ❌ Most complex architecture
- ❌ Requires multi-site infrastructure
- ❌ Cross-site networking complexity
- ❌ Higher operational overhead
- ❌ Multi-hub coordination

---

## 📊 Comparison Matrix

| Feature                     | Single Cluster | Multi-Cluster (No ACM) | Multi-Cluster (ACM) | Multi-Site (ACM) |
| --------------------------- | -------------- | ---------------------- | ------------------- | ---------------- |
| **Clusters**                | 1              | 2-5                    | 6+                  | 10+              |
| **Management Overhead**     | Low            | Medium                 | Medium              | High             |
| **Setup Complexity**        | Simple         | Medium                 | High                | Very High        |
| **Centralized Control**     | ❌             | ❌                     | ✅                  | ✅               |
| **Policy Enforcement**      | ❌             | ❌                     | ✅                  | ✅               |
| **Fleet-wide Updates**      | N/A            | Manual                 | Automated           | Automated        |
| **Disaster Recovery**       | ❌             | Manual                 | ✅                  | ✅✅             |
| **Geographic Distribution** | ❌             | ⚠️                     | ⚠️                  | ✅               |
| **Initial Setup Time**      | 30 min         | 1-2 hours              | 2-3 hours           | 4+ hours         |
| **Per-Cluster Time**        | N/A            | 1 hour                 | 30 min              | 30 min           |
| **Recommended For**         | Testing        | Small teams            | Large teams         | Enterprises      |

---

## 🏗️ Architecture Diagrams

### Single Cluster

```
┌─────────────────────────────────────┐
│        OpenShift Cluster            │
│  ┌───────────────────────────────┐  │
│  │   OpenShift GitOps (Argo CD)  │  │
│  └───────────────┬───────────────┘  │
│                  │                   │
│                  ▼                   │
│  ┌───────────────────────────────┐  │
│  │  Applications & Platform      │  │
│  │  - AI Stack                   │  │
│  │  - Media Stack                │  │
│  │  - Platform Components        │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Git Repository │
│  (values files) │
└─────────────────┘
```

### Multi-Cluster without ACM

```
┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│   Cluster 1 (Dev)    │   │   Cluster 2 (Test)   │   │   Cluster 3 (Prod)   │
│ ┌──────────────────┐ │   │ ┌──────────────────┐ │   │ ┌──────────────────┐ │
│ │ OpenShift GitOps │ │   │ │ OpenShift GitOps │ │   │ │ OpenShift GitOps │ │
│ └────────┬─────────┘ │   │ └────────┬─────────┘ │   │ └────────┬─────────┘ │
│          │           │   │          │           │   │          │           │
│          ▼           │   │          ▼           │   │          ▼           │
│ ┌──────────────────┐ │   │ ┌──────────────────┐ │   │ ┌──────────────────┐ │
│ │  Applications    │ │   │ │  Applications    │ │   │ │  Applications    │ │
│ └──────────────────┘ │   │ └──────────────────┘ │   │ └──────────────────┘ │
└──────────────────────┘   └──────────────────────┘   └──────────────────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
                           ┌─────────────────┐
                           │  Git Repository │
                           │  - values-dev   │
                           │  - values-test  │
                           │  - values-prod  │
                           └─────────────────┘
```

### Multi-Cluster with ACM

```
                    ┌─────────────────────────────────┐
                    │      Hub Cluster (ACM)          │
                    │ ┌─────────────────────────────┐ │
                    │ │ Advanced Cluster Management │ │
                    │ └─────────────┬───────────────┘ │
                    │               │                 │
                    └───────────────┼─────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ Managed Cluster 1│  │ Managed Cluster 2│  │ Managed Cluster 3│
    │ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │
    │ │ Applications │ │  │ │ Applications │ │  │ │ Applications │ │
    │ └──────────────┘ │  │ └──────────────┘ │  │ └──────────────┘ │
    └──────────────────┘  └──────────────────┘  └──────────────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  Git Repository │
                           └─────────────────┘
```

### Multi-Site with ACM

```
Site 1 (US East)                            Site 2 (EU West)
┌─────────────────────────────┐             ┌─────────────────────────────┐
│    Hub Cluster (US-East)    │             │    Hub Cluster (EU-West)    │
│ ┌─────────────────────────┐ │             │ ┌─────────────────────────┐ │
│ │          ACM            │ │◄───────────►│ │          ACM            │ │
│ └────────────┬────────────┘ │             │ └────────────┬────────────┘ │
│              │              │             │              │              │
└──────────────┼──────────────┘             └──────────────┼──────────────┘
               │                                           │
       ┌───────┴────────┐                         ┌───────┴────────┐
       ▼                ▼                         ▼                ▼
┌─────────────┐  ┌─────────────┐         ┌─────────────┐  ┌─────────────┐
│ Managed     │  │ Managed     │         │ Managed     │  │ Managed     │
│ Cluster 1   │  │ Cluster 2   │         │ Cluster 3   │  │ Cluster 4   │
└─────────────┘  └─────────────┘         └─────────────┘  └─────────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  Git Repository │
                                        │  (Multi-region) │
                                        └─────────────────┘
```

---

## 🔑 Key Considerations

### When to Choose Single Cluster

- **Learning:** You're new to OpenShift GitOps or Validated Patterns
- **Testing:** Validating applications before production
- **Small Scale:** Single application or simple workload
- **Budget:** Limited infrastructure resources
- **Speed:** Need to deploy quickly

### When to Choose Multi-Cluster (No ACM)

- **Independence:** Each cluster has unique requirements
- **Control:** Direct per-cluster management preferred
- **Simplicity:** Team comfortable with manual operations
- **Scale:** 2-5 clusters maximum
- **Cost:** Avoiding ACM licensing/infrastructure

### When to Choose Multi-Cluster (ACM)

- **Scale:** 6+ clusters to manage
- **Automation:** Prefer automated provisioning/management
- **Governance:** Need policy-based compliance
- **Consistency:** Fleet-wide application deployment
- **Efficiency:** Reduce operational overhead

### When to Choose Multi-Site (ACM)

- **DR:** Disaster recovery requirements
- **Geography:** Users in multiple regions
- **Compliance:** Data residency regulations
- **Availability:** Multi-region high availability
- **Scale:** Enterprise-wide deployment

---

## � Environment-Specific Configuration

### Cluster Sets

The pattern supports three primary cluster sets with different infrastructure assumptions:

#### Home Lab (Primary Focus - Fully Supported)

- **Infrastructure:** Hub, Test, and Prod clusters with shared infrastructure
- **Platform Components:**
  - External Secrets Operator (Infisical backend)
  - cert-manager (Let's Encrypt + Cloudflare DNS)
  - TrueNAS storage
  - Keepalived
  - Goldilocks, VPA, Gatus
  - Generic Device Plugin
  - Node Feature Discovery
  - System Reservation
  - ArgoCD resource config updates
  - Snapshot finalizer remover
- **Prod Cluster Additions:** Media applications
- **Test Cluster:** Platform without Keepalived or Kasten, adds MetalLB and Paperless
- **Secrets:** Single Infisical project/environment shared across home clusters
- **Certificates:** Let's Encrypt with Cloudflare DNS validation
- **Values Files:** `values-global.yaml` + `clusters/sets/values-home.yaml` + `clusters/individual-clusters/values-{cluster}.yaml`

#### Work Lab (Secondary Focus - Future Support)

- **Infrastructure:** Separate lab environment with different storage/networking
- **Platform Components:** All except TrueNAS (uses ODF or enterprise storage)
- **Secrets:** Different Infisical project or alternative secret backend
- **Certificates:** Internal CA or different ACME provider
- **Values Files:** `values-global.yaml` + `clusters/sets/values-worklab.yaml` + `clusters/topologies/values-{topology}.yaml` + `values-{cluster}.yaml`

#### Cloud (Stretch Goal - Future Support)

- **Providers:** ROSA, ARO, IBM Cloud OpenShift (TechZone)
- **Platform Components:** Minimal - prefer cloud-managed services
- **Storage:** Cloud-native (EBS, Azure Disk, IBM Cloud Block)
- **Secrets:** Cloud secret manager (AWS Secrets Manager, Azure Key Vault, IBM Secrets Manager)
- **Certificates:** Cloud certificate manager or Let's Encrypt with cloud DNS
- **Values Files:** `values-global.yaml` + `clusters/sets/values-cloud.yaml` + `values-{provider}.yaml` + `values-{cluster}.yaml`

### Topology Options

#### Single Node OpenShift (SNO)

- **Use Case:** Edge deployments, small environments, home lab, dev/test
- **Characteristics:**
  - Single replica (no HA)
  - Minimal resource requests
  - No PodDisruptionBudgets
  - Combined control plane + worker
- **Cluster Examples:** `values-prod.yaml`, `values-test.yaml`

#### Compact (3-node)

- **Use Case:** Small production, branch offices
- **Characteristics:**
  - 2-3 replicas
  - PDBs configured for single node maintenance
  - Control plane nodes run workloads
  - Small resource requests
- **Values File:** `clusters/topologies/values-compact.yaml`

#### Full Cluster (6+ nodes)

- **Use Case:** Production clusters, large deployments
- **Characteristics:**
  - 3+ replicas for HA
  - Standard PDBs (minAvailable: 2)
  - Dedicated control plane nodes
  - Standard resource requests
- **Values File:** `clusters/topologies/values-full.yaml`

### Certificate Provider Configuration

#### Home Lab - Let's Encrypt + Cloudflare DNS

```yaml
certificates:
  provider: letsencrypt
  letsencrypt:
    issuer: production
    email: your-email@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    dns:
      provider: cloudflare
      apiTokenSecretRef: cloudflare-api-token
```

#### Work Lab - Internal CA or Different ACME

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

#### Cloud - Cloud Certificate Manager

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

### External Secrets Provider Configuration

#### Home Lab - Infisical

```yaml
externalSecrets:
  provider: infisical
  secret: infisical-auth-secret
  infisical:
    projectSlug: hub
    environmentSlug: prod
    apiUrl: https://app.infisical.com
```

#### Work Lab - Different Infisical Project or Vault

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

#### Cloud - Cloud Secret Manager

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

### Multi-Hub Architecture

For high availability and blast radius reduction:

#### Same Datacenter - Multiple Hubs

```text
Hub1 (hub1.example.com)
  ├── sno (production-1)
  ├── test (dev-1)
  └── compact-1

Hub2 (hub2.example.com)
  ├── sno (production-2)
  ├── compact-2
  └── full-1
```

**Configuration:**

- Each hub has ACM/MCE enabled
- Managed clusters target specific hub
- Shared or separate Infisical projects
- Consistent certificate provider

#### Geographic Distribution

```text
Hub-East (hub-east.example.com)
  ├── cluster1-east
  ├── cluster2-east
  └── cluster3-east

Hub-West (hub-west.example.com)
  ├── cluster1-west
  ├── cluster2-west
  └── cluster3-west
```

**Configuration:**

- Region-specific values files
- Regional certificate providers
- Regional secret backends
- Geographic load balancing

### Values File Hierarchy Examples

```bash
# Home Lab - Production cluster (SNO)
helm install prod ./roles/sno \
  -f values-global.yaml \
  -f clusters/sets/values-home.yaml \
  -f clusters/individual-clusters/values-prod.yaml

# Work Lab - Compact cluster
helm install compact1 ./roles/compact \
  -f values-global.yaml \
  -f clusters/sets/values-worklab.yaml \
  -f clusters/topologies/values-compact.yaml \
  -f values-compact1.yaml

# Cloud - Full cluster (ROSA)
helm install prod-rosa ./roles/full \
  -f values-global.yaml \
  -f clusters/sets/values-cloud.yaml \
  -f clusters/sets/values-cloud-rosa.yaml \
  -f clusters/topologies/values-full.yaml \
  -f clusters/individual-clusters/values-prod-rosa.yaml
```

---

## �📝 Next Steps

1. **Review your requirements:**

   - Number of clusters needed
   - Geographic distribution
   - Management complexity tolerance
   - Team expertise level

2. **Choose your deployment pattern** using the decision tree above

3. **Follow the appropriate quick start guide:**

   - [Single Cluster Quick Start](./single-cluster-quickstart.md)
   - [Multi-Cluster Quick Start](./multi-cluster-quickstart.md)
   - [ACM Quick Start](./acm-quickstart.md)
   - [Multi-Site Quick Start](./multi-site-quickstart.md)

4. **Configure your environment:**

   - Set up Git repository
   - Prepare values files
   - Configure secrets management

5. **Deploy and validate:**
   - Follow deployment instructions
   - Verify application deployment
   - Test cluster operations

---

## 📚 Related Documentation

- [Getting Started Guide](../../GETTING-STARTED.md)
- [Architecture Overview](../DETAILED-OVERVIEW.md)
- [Values Hierarchy](../VALUES-HIERARCHY.md)
- [Configuration Guide](../CONFIGURATION-GUIDE.md)
- [ACM Getting Started](../ACM-GETTING-STARTED.md)
- [ADR 008: Multi-Cluster Strategy](../decisions/008-multi-cluster-management-strategy.md)
- [Documentation Index](../INDEX.md)

---

**Last Updated:** 2025-01-27
**Maintained By:** Repository maintainers
