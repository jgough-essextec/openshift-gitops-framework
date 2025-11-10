# Values File Hierarchy and Usage

> **📋 Strategic Context:** See [ADR 005: Values Hierarchy Pattern](./decisions/005-values-hierarchy-pattern.md) for the architectural decision and rationale behind the hierarchical values system.

This document explains how to use the values files for different deployment scenarios.

## Values File Structure

The pattern uses a **hierarchical values system** that allows configuration at multiple levels:

```
values-global.yaml (pattern defaults)
  ├── clusters/sets/values-home.yaml      # Home lab cluster set (TrueNAS, Cloudflare, Infisical)
  │   ├── clusters/individual-clusters/values-prod.yaml        # Production cluster (SNO topology)
  │   ├── clusters/individual-clusters/values-test.yaml        # Test/dev cluster (SNO topology)
  │   └── clusters/individual-clusters/values-hub.yaml         # Hub management cluster
  ├── clusters/sets/values-worklab.yaml   # Work lab cluster set (no TrueNAS, different certs)
  │   ├── clusters/topologies/values-compact.yaml     # Compact topology (2-3 replicas, PDBs)
  │   └── clusters/topologies/values-full.yaml        # Full HA topology (3+ replicas)
  └── clusters/sets/values-cloud.yaml     # Cloud cluster set (ROSA, ARO, IBM Cloud)
      └── values-{cluster}.yaml  # Cloud-specific cluster config
```

**Note:** The `charts/topology/` directory structure has been removed (ADR 003) as it provided no value. Topology configuration belongs in values files, not chart directories.

## Deployment Examples

### Home Lab - Production Cluster

```bash
# Deploy production cluster (SNO topology)
helm install prod ./roles/sno \
  -f values-global.yaml \
  -f clusters/sets/values-home.yaml \
  -f clusters/individual-clusters/values-prod.yaml \
  -n openshift-gitops

# What each file provides:
# - values-global.yaml: Pattern defaults (GitOps repo, image registry, etc.)
# - clusters/sets/values-home.yaml: Home lab specifics (TrueNAS, Infisical, Let's Encrypt)
# - clusters/individual-clusters/values-prod.yaml: Production cluster config (uses SNO topology, enabled apps)
```

### Home Lab - Hub Cluster

```bash
# Deploy Hub management cluster with ACM/MCE
helm install hub ./roles/hub \
  -f clusters/sets/values-home.yaml \
  -f clusters/individual-clusters/values-hub.yaml \
  -f values-global.yaml

# Precedence: values-global.yaml → values-home.yaml → values-hub.yaml
# - clusters/sets/values-home.yaml: Home lab specifics
# - clusters/individual-clusters/values-hub.yaml: Hub topology + ACM/MCE enabled
```

### Home Lab - Test Cluster

```bash
# Deploy Test/Dev cluster
helm install test ./roles/sno \
  -f clusters/sets/values-home.yaml \
  -f clusters/individual-clusters/values-test.yaml \
  -f values-global.yaml

# Precedence: values-global.yaml → values-home.yaml → values-test.yaml
# - clusters/sets/values-home.yaml: Home lab specifics
# - clusters/individual-clusters/values-test.yaml: Test cluster config (uses SNO topology, minimal apps)
```

### Work Lab - Compact Cluster

```bash
helm install compact ./roles/compact \
  -f clusters/sets/values-worklab.yaml \
  -f clusters/topologies/values-compact.yaml \
  -f values-global.yaml

# Precedence: values-global.yaml → values-worklab.yaml → values-compact.yaml
# - clusters/sets/values-worklab.yaml: Work lab specifics (no TrueNAS, different certs)
# - clusters/topologies/values-compact.yaml: Compact topology (2-3 replicas, PDBs)
```

### Cloud - ROSA Full Cluster

```bash
# Deploy ROSA full cluster
helm install full ./roles/full \
  -f clusters/sets/values-cloud.yaml \
  -f values-global.yaml \
  -f clusters/topologies/values-full.yaml \
  -f values-custom.yaml

# Precedence: values-global.yaml → values-cloud.yaml → values-full.yaml → values-custom.yaml
# - clusters/sets/values-cloud.yaml: Cloud defaults (minimal platform)
# - values-global.yaml: Pattern defaults
# - clusters/topologies/values-full.yaml: Full HA topology (3+ replicas, standard PDBs)
```

## Configuration Layers

### Layer 1: Global Defaults (`values-global.yaml`)

Defines pattern-wide settings that apply to ALL clusters:

- Pattern name and version
- GitOps repository configuration
- Image registry defaults
- Common component defaults

**When to edit:** Almost never. These are foundational pattern settings.

### Layer 2: Cluster Set (`values-{home|worklab|cloud}.yaml`)

Defines environment-specific defaults:

**Home Lab (`clusters/sets/values-home.yaml`):**

- TrueNAS storage configuration
- Let's Encrypt with Cloudflare DNS
- Infisical for secrets
- All platform components enabled by default
- AMD Radeon Vega 8 GPU configuration

**Work Lab (`clusters/sets/values-worklab.yaml`):**

- ODF or enterprise storage
- Internal CA or different ACME provider
- Vault or different secret backend
- Most platform components enabled (no TrueNAS)

**Cloud (`clusters/sets/values-cloud.yaml`):**

- Cloud-managed storage (EBS, Azure Disk, etc.)
- Cloud certificate manager or Let's Encrypt with cloud DNS
- Cloud secret manager
- Minimal platform components (leverage cloud services)

**When to edit:** When adding new cluster sets or changing environment-wide defaults.

### Layer 3: Topology (`values-{sno|compact|full|hub}.yaml`)

Defines cluster size/topology-specific settings:

**SNO Topology (used by individual cluster files):**

- Single replica (no HA)
- Minimal resource requests
- No PodDisruptionBudgets
- Single node tolerations
- Deployed via roles/sno/

**Compact (`clusters/topologies/values-compact.yaml`):**

- 2-3 replicas
- Small resource requests
- PDBs allowing single node maintenance
- Control plane node tolerations

**Full (`clusters/topologies/values-full.yaml`):**

- 3+ replicas for HA
- Standard resource requests
- Standard PDBs (minAvailable: 2)
- Worker node scheduling

**Hub (`clusters/individual-clusters/values-hub.yaml`):**

- ACM/MCE enabled
- No application workloads by default
- Management cluster configuration

**When to edit:** When defining new topology patterns or changing replica/resource defaults.

### Layer 4: Individual Cluster (`values-{cluster-name}.yaml`)

Defines cluster-specific overrides:

- Cluster name and domain
- Storage prefixes (e.g., `sno-`, `hub-`, `test-`)
- Network configuration (IPs, subnets)
- Enabled applications
- Node names for GPU labeling
- Backup configuration
- Managed clusters (for hub)

**When to edit:** For each new cluster or when changing cluster-specific settings.

## Certificate Configuration Examples

### Home Lab - Let's Encrypt + Cloudflare

```yaml
# values-home.yaml
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

### Work Lab - Internal CA

```yaml
# clusters/sets/values-worklab.yaml
certificates:
  provider: internal-ca
  internalCA:
    issuerRef: corporate-ca
    duration: 2160h # 90 days
```

### Work Lab - Let's Encrypt + Route53

```yaml
# clusters/sets/values-worklab.yaml
certificates:
  provider: letsencrypt
  letsencrypt:
    issuer: production
    dns:
      provider: route53
      region: us-east-1
      hostedZoneID: Z1234567890ABC
```

### Cloud - AWS Certificate Manager

```yaml
# values-cloud-rosa.yaml
certificates:
  provider: aws-acm
  aws:
    region: us-east-1
    certificateArn: arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012
```

## External Secrets Configuration Examples

### Home Lab - Infisical

```yaml
# clusters/sets/values-home.yaml
externalSecrets:
  provider: infisical
  secret: infisical-auth-secret
  infisical:
    projectSlug: hub
    environmentSlug: prod
    apiUrl: https://app.infisical.com
```

### Work Lab - HashiCorp Vault

```yaml
# clusters/sets/values-worklab.yaml
externalSecrets:
  provider: vault
  secret: vault-auth-secret
  vault:
    server: https://vault.corporate.com
    namespace: engineering
    authPath: kubernetes
    role: openshift-gitops
```

### Cloud - AWS Secrets Manager

```yaml
# values-cloud-rosa.yaml
externalSecrets:
  provider: aws-secrets-manager
  aws:
    region: us-east-1
    roleArn: arn:aws:iam::123456789012:role/openshift-external-secrets
```

## Application Configuration Examples

### Cluster-Level Application Configuration

```yaml
# values-prod.yaml
applicationStacks:
  media:
    enabled: true
    apps:
      plex:
        enabled: true
        loadBalancerIP: 192.168.1.200
        storage:
          size: 500Gi
      sonarr:
        enabled: true
        loadBalancerIP: 192.168.1.201
```

### Namespace-Level Application Configuration

```yaml
# clusters/individual-clusters/values-prod.yaml
applications:
  plex:
    namespace: plex
    labels:
      environment: production
      backup: "true"
    config:
      transcoding:
        enabled: true
        gpu: amd
      library:
        path: /mnt/media
```

## Storage Configuration Examples

### Home Lab - TrueNAS

```yaml
# clusters/sets/values-home.yaml
storage:
  default:
    provider: truenas
    className: truenas-iscsi
  truenas:
    enabled: true
    server: truenas.roybales.com
    iscsi:
      portal: truenas.roybales.com:3260
      namePrefix: home- # Override per cluster: sno-, hub-, test-
```

### Work Lab - ODF

```yaml
# values-worklab.yaml
storage:
  default:
    provider: odf
    className: ocs-storagecluster-ceph-rbd
  odf:
    enabled: true
    nodeCount: 3
```

### Cloud - AWS EBS

```yaml
# values-cloud-rosa.yaml
storage:
  default:
    provider: ebs
    className: gp3
  ebs:
    type: gp3
    encrypted: true
```

## Platform-Only vs Apps-Only Deployment

### Deploy Platform Only

```yaml
# In cluster values file
platformComponents:
  # ... all platform components enabled

applicationStacks:
  ai:
    enabled: false
  media:
    enabled: false
  homeAutomation:
    enabled: false
  productivity:
    enabled: false
```

### Deploy Apps Only

```yaml
# In cluster values file
platformComponents:
  # ... all platform components disabled (assume already deployed)
  externalSecrets:
    enabled: false
  certManager:
    enabled: false
  # ... etc

applicationStacks:
  ai:
    enabled: true
  media:
    enabled: true
  # ... etc
```

## Multi-Hub Configuration

### Hub1 - East Coast

```yaml
# values-hub1-east.yaml
clusterGroup:
  name: hub1-east
  topology: hub
  clusterSet: home
  region: us-east

platformComponents:
  acm:
    enabled: true
  multiclusterEngine:
    enabled: true

managedClusters:
  - name: sno-east-1
    region: us-east
  - name: compact-east-1
    region: us-east
```

### Hub2 - West Coast

```yaml
# values-hub2-west.yaml
clusterGroup:
  name: hub2-west
  topology: hub
  clusterSet: home
  region: us-west

platformComponents:
  acm:
    enabled: true
  multiclusterEngine:
    enabled: true

managedClusters:
  - name: sno-west-1
    region: us-west
  - name: compact-west-1
    region: us-west
```

## Best Practices

1. **Never edit `values-global.yaml`** unless changing pattern-wide defaults
2. **Edit cluster set files (`clusters/sets/values-home.yaml`)** for environment-wide changes
3. **Topology settings are in roles/\*/values.yaml** - not in cluster values files
4. **Create new cluster files (`values-{cluster}.yaml`)** for each cluster
5. **Use meaningful cluster names** that indicate purpose and location
6. **Document overrides** with comments explaining why they differ from defaults
7. **Test on non-production clusters first** (test cluster in home lab)
8. **Commit cluster values files** to Git for version control and GitOps

## Troubleshooting

### Values Not Taking Effect

1. Check the order of `-f` flags (later files override earlier ones)
2. Verify the correct values file is being used
3. Check for typos in YAML keys
4. Use `helm template` to see the rendered output

### Conflicts Between Values Files

1. Later files in the `-f` list override earlier files
2. Use `helm template --debug` to see which values are being used
3. Check for conflicting keys between files

### Application Not Deploying

1. Check if `enabled: true` at all levels (global, cluster set, topology, cluster)
2. Verify ApplicationSet is created: `oc get applicationset -n openshift-gitops`
3. Check Application status: `oc get application <app> -n openshift-gitops`
4. Check ArgoCD UI for sync errors

## Reference

- **Deployment Options:** [docs/deployment/DEPLOYMENT-OPTIONS.md](./deployment/DEPLOYMENT-OPTIONS.md)
- **Configuration Guide:** [docs/CONFIGURATION-GUIDE.md](./CONFIGURATION-GUIDE.md)
- **Architecture Decision Records:** [docs/decisions/](./decisions/)
- **Cluster Bootstrap:** [docs/operations/CLUSTER-BOOTSTRAP.md](./operations/CLUSTER-BOOTSTRAP.md)
- **Chart Documentation:** [charts/README.md](./charts/README.md)
