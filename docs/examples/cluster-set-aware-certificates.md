# Cluster-Set Aware Certificate Management

This document demonstrates how to implement cluster-set aware certificate provider selection, allowing different certificate management strategies based on environment (Home/Work Lab/Cloud).

## Overview

Different cluster sets require different certificate providers:

- **Home Lab**: Cloudflare DNS-01 challenge (public domain, home infrastructure)
- **Work Lab**: Internal CA or different DNS provider (corporate policies)
- **Cloud**: Cloud-native DNS (Route53 for AWS, Azure DNS, Google Cloud DNS)

## Implementation Strategy

### 1. Add Cluster Set Configuration

Update values files with cluster set identification:

**values-home.yaml:**

```yaml
clusterSet:
  name: home
  description: "Home lab infrastructure"

certificates:
  provider: cloudflare
  cloudflare:
    email: admin@example.com
    apiTokenSecret: cloudflare-api-token
    apiTokenSecretKey: api-token

  issuer:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
```

**values-worklab.yaml:**

```yaml
clusterSet:
  name: worklab
  description: "Work lab infrastructure"

certificates:
  provider: internal-ca
  internalCA:
    secretName: work-ca-cert
    secretKey: tls.crt

  issuer:
    server: https://acme.corp.example.com/directory
    email: acme@corp.example.com
```

**values-cloud.yaml:**

```yaml
clusterSet:
  name: cloud
  description: "Cloud infrastructure"

cloud:
  provider: aws # or azure, gcp
  region: us-east-1

certificates:
  provider: route53
  route53:
    region: us-east-1
    hostedZoneID: Z1234567890ABC
    # Uses IAM role via IRSA

  issuer:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: cloud-admin@example.com
```

### 2. Update Certificate Chart

**charts/platform/certificates/values.yaml:**

```yaml
# Default values - overridden by cluster-set values
certificates:
  enabled: true

  # Provider selection (cloudflare, route53, azureDNS, googleCloudDNS, internal-ca)
  provider: cloudflare

  # Cloudflare DNS-01 (Home Lab)
  cloudflare:
    email: ""
    apiTokenSecret: cloudflare-api-token
    apiTokenSecretKey: api-token

  # AWS Route53 DNS-01 (Cloud - AWS)
  route53:
    region: us-east-1
    hostedZoneID: ""
    # IAM role via IRSA for authentication
    irsaRoleArn: ""

  # Azure DNS DNS-01 (Cloud - Azure)
  azureDNS:
    subscriptionID: ""
    tenantID: ""
    resourceGroupName: ""
    hostedZoneName: ""
    # Managed identity for authentication
    managedIdentityClientID: ""

  # Google Cloud DNS DNS-01 (Cloud - GCP)
  googleCloudDNS:
    project: ""
    # Workload Identity for authentication
    serviceAccountEmail: ""

  # Internal CA (Work Lab)
  internalCA:
    secretName: internal-ca-cert
    secretKey: tls.crt

  # Issuer configuration
  issuer:
    name: letsencrypt-prod
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ""
```

**charts/platform/certificates/templates/cluster-issuer-cloudflare.yaml:**

```yaml
{{- if eq .Values.certificates.provider "cloudflare" }}
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: {{ .Values.certificates.issuer.name }}
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  acme:
    server: {{ .Values.certificates.issuer.server }}
    email: {{ .Values.certificates.issuer.email }}
    privateKeySecretRef:
      name: {{ .Values.certificates.issuer.name }}-account-key
    solvers:
    - dns01:
        cloudflare:
          email: {{ .Values.certificates.cloudflare.email }}
          apiTokenSecretRef:
            name: {{ .Values.certificates.cloudflare.apiTokenSecret }}
            key: {{ .Values.certificates.cloudflare.apiTokenSecretKey }}
{{- end }}
```

**charts/platform/certificates/templates/cluster-issuer-route53.yaml:**

```yaml
{{- if eq .Values.certificates.provider "route53" }}
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: {{ .Values.certificates.issuer.name }}
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  acme:
    server: {{ .Values.certificates.issuer.server }}
    email: {{ .Values.certificates.issuer.email }}
    privateKeySecretRef:
      name: {{ .Values.certificates.issuer.name }}-account-key
    solvers:
    - dns01:
        route53:
          region: {{ .Values.certificates.route53.region }}
          hostedZoneID: {{ .Values.certificates.route53.hostedZoneID }}
          {{- if .Values.certificates.route53.irsaRoleArn }}
          auth:
            kubernetes:
              serviceAccountRef:
                name: cert-manager
          {{- end }}
{{- end }}
```

**charts/platform/certificates/templates/cluster-issuer-azure.yaml:**

```yaml
{{- if eq .Values.certificates.provider "azureDNS" }}
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: {{ .Values.certificates.issuer.name }}
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  acme:
    server: {{ .Values.certificates.issuer.server }}
    email: {{ .Values.certificates.issuer.email }}
    privateKeySecretRef:
      name: {{ .Values.certificates.issuer.name }}-account-key
    solvers:
    - dns01:
        azureDNS:
          subscriptionID: {{ .Values.certificates.azureDNS.subscriptionID }}
          tenantID: {{ .Values.certificates.azureDNS.tenantID }}
          resourceGroupName: {{ .Values.certificates.azureDNS.resourceGroupName }}
          hostedZoneName: {{ .Values.certificates.azureDNS.hostedZoneName }}
          managedIdentity:
            clientID: {{ .Values.certificates.azureDNS.managedIdentityClientID }}
{{- end }}
```

**charts/platform/certificates/templates/cluster-issuer-internal-ca.yaml:**

```yaml
{{- if eq .Values.certificates.provider "internal-ca" }}
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: {{ .Values.certificates.issuer.name }}
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  ca:
    secretName: {{ .Values.certificates.internalCA.secretName }}
{{- end }}
```

### 3. External Secrets Operator Integration

For cloud environments, create cluster-set aware secret stores:

**charts/platform/external-secrets-operator/templates/cluster-secret-store.yaml:**

```yaml
{{- if eq .Values.clusterSet.name "home" }}
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: infisical
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  provider:
    infisical:
      serverURL: {{ .Values.externalSecrets.infisical.serverUrl }}
      auth:
        universalAuthCredentials:
          clientId:
            secretRef:
              name: infisical-auth
              key: client-id
          clientSecret:
            secretRef:
              name: infisical-auth
              key: client-secret
{{- else if eq .Values.clusterSet.name "worklab" }}
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  provider:
    vault:
      server: {{ .Values.externalSecrets.vault.vaultUrl }}
      path: {{ .Values.externalSecrets.vault.path }}
      version: v2
      auth:
        kubernetes:
          mountPath: kubernetes
          role: external-secrets
{{- else if eq .Values.clusterSet.name "cloud" }}
  {{- if eq .Values.cloud.provider "aws" }}
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  provider:
    aws:
      service: SecretsManager
      region: {{ .Values.cloud.region }}
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-operator
  {{- else if eq .Values.cloud.provider "azure" }}
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: azure-keyvault
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  provider:
    azurekv:
      vaultUrl: {{ .Values.externalSecrets.azure.vaultUrl }}
      authType: ManagedIdentity
      identityId: {{ .Values.externalSecrets.azure.managedIdentityClientID }}
  {{- end }}
{{- end }}
```

### 4. Usage in Application Charts

Applications automatically use the correct certificate provider:

**charts/applications/media/plex/templates/route.yaml:**

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: { { include "plex.fullname" . } }
  annotations:
    # Certificate will be issued by cluster-set appropriate ClusterIssuer
    cert-manager.io/cluster-issuer:
      {
        {
          .Values.global.certificates.issuer.name | default "letsencrypt-prod",
        },
      }
spec:
  host: { { .Values.route.host } }
  to:
    kind: Service
    name: { { include "plex.fullname" . } }
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

## Testing Scenarios

### Home Lab (Cloudflare)

```bash
# Deploy with Cloudflare DNS-01
helm install sno ./roles/sno \
  -f values-global.yaml \
  -f values-home.yaml \
  -f values-sno.yaml \
  -n openshift-gitops

# Verify ClusterIssuer
oc get clusterissuer letsencrypt-prod -o yaml

# Should show Cloudflare solver configuration
```

### Work Lab (Internal CA)

```bash
# Deploy with internal CA
helm install worklab-compact ./roles/compact \
  -f values-global.yaml \
  -f values-worklab.yaml \
  -f values-compact.yaml \
  -n openshift-gitops

# Verify ClusterIssuer
oc get clusterissuer letsencrypt-prod -o yaml

# Should show CA issuer configuration
```

### Cloud AWS (Route53)

```bash
# Deploy with Route53 DNS-01
helm install rosa-prod ./roles/compact \
  -f values-global.yaml \
  -f values-cloud.yaml \
  -f values-rosa-prod.yaml \
  -n openshift-gitops

# Verify ClusterIssuer
oc get clusterissuer letsencrypt-prod -o yaml

# Should show Route53 solver with IRSA
```

## Benefits

1. **Environment Awareness**: Certificates automatically use appropriate provider
2. **No Manual Configuration**: Provider selection based on cluster-set values
3. **Flexibility**: Easy to add new providers or cluster sets
4. **Security**: Each environment uses appropriate authentication method
5. **Consistency**: All apps use same issuer, configured once

## Migration Path

### Phase 1: Add Cluster Set Config

- Add `clusterSet.name` to all values files
- Add provider-specific configuration

### Phase 2: Update Certificate Chart

- Add conditional ClusterIssuer templates
- Test in each environment

### Phase 3: Validate Applications

- Ensure Routes/Ingresses reference correct issuer
- Verify certificates are issued successfully

### Phase 4: Add ESO Integration

- Create cluster-set aware ClusterSecretStores
- Migrate secrets to appropriate backend

## Future Enhancements

1. **Multiple Issuers**: Support both staging and production ACME servers
2. **Hybrid Providers**: Mix internal CA and public ACME in same cluster
3. **Cost Optimization**: Use HTTP-01 for cloud environments (avoid DNS API costs)
4. **Certificate Monitoring**: Integrate with Gatus for expiration monitoring
5. **Auto-Renewal Testing**: Automated validation of renewal processes

## References

- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Cloudflare DNS-01 Solver](https://cert-manager.io/docs/configuration/acme/dns01/cloudflare/)
- [AWS Route53 DNS-01 Solver](https://cert-manager.io/docs/configuration/acme/dns01/route53/)
- [Azure DNS DNS-01 Solver](https://cert-manager.io/docs/configuration/acme/dns01/azuredns/)
- [External Secrets Operator](https://external-secrets.io/)
- ADR 003: Simplify Cluster Topology Structure
