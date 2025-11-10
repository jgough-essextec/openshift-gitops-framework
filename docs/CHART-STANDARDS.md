# Application Helm Chart Best Practices & Standards

> **📋 Strategic Context:** See [ADR 006: Chart Standards & Security](./decisions/006-chart-standards-and-security.md) for the architectural decision and rationale behind these standards.

This document defines the well-architected framework for application Helm charts in this repository.

## Core Principles

1. **Keep Charts Boring** - Use standard, well-understood patterns. No clever tricks.
2. **Portable** - Charts should work on vanilla Kubernetes AND OpenShift
3. **OpenShift-Aware** - Default to OpenShift conventions, make Kubernetes features optional
4. **Namespace-Scoped** - Apps should never require cluster-level permissions
5. **CRDs Co-located** - Application-specific CRDs belong in the app's chart `/crds/` directory
6. **Platform Separation** - Cluster-level resources (SCCs, ClusterRoles, storage classes) belong in platform charts

## Required Chart Structure

Every application chart MUST follow this structure:

```
charts/applications/{domain}/{app-name}/
├── Chart.yaml                    # Required - Chart metadata
├── values.yaml                   # Required - Default values
├── values.schema.json            # Recommended - JSON schema for values validation
├── README.md                     # Required - Usage documentation
├── crds/                         # Optional - Application-specific CRDs only
│   └── myapp.crd.yaml
├── templates/
│   ├── NOTES.txt                 # Required - Post-install instructions
│   ├── _helpers.tpl              # Recommended - Template helpers
│   ├── deployment.yaml           # Required - Workload (or statefulset.yaml)
│   ├── service.yaml              # Required - Service
│   ├── serviceaccount.yaml       # Required - ServiceAccount
│   ├── role.yaml                 # Optional - RBAC Role (namespace-scoped only)
│   ├── rolebinding.yaml          # Optional - RBAC RoleBinding
│   ├── route.yaml                # Recommended - OpenShift Route (default)
│   ├── ingress.yaml              # Optional - Kubernetes Ingress (opt-in)
│   ├── configmap.yaml            # Optional - Configuration
│   ├── secret.yaml               # Optional - Non-sensitive defaults only
│   ├── externalsecret.yaml       # Recommended - External Secrets Operator integration
│   ├── pvc.yaml                  # Optional - Persistent storage
│   ├── hpa.yaml                  # Optional - Horizontal Pod Autoscaler
│   ├── pdb.yaml                  # Optional - Pod Disruption Budget
│   ├── networkpolicy.yaml        # Recommended - Network isolation
│   ├── servicemonitor.yaml       # Optional - Prometheus monitoring
│   └── consolelink.yaml          # Optional - OpenShift Console integration
└── tests/
    └── test-connection.yaml      # Recommended - Helm test
```

## Mandatory Templates

### 1. Deployment/StatefulSet

**Use Deployment for stateless apps, StatefulSet for stateful apps.**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: { { include "app.fullname" . } }
  namespace: { { .Release.Namespace } }
  labels: { { - include "app.labels" . | nindent 4 } }
spec:
  replicas: { { .Values.replicaCount } }
  selector:
    matchLabels: { { - include "app.selectorLabels" . | nindent 6 } }
  template:
    metadata:
      labels: { { - include "app.selectorLabels" . | nindent 8 } }
    spec:
      serviceAccountName: { { include "app.serviceAccountName" . } }
      securityContext:
        # OpenShift-compatible: works under restricted SCC
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: { { .Chart.Name } }
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: { { .Values.image.pullPolicy } }
          securityContext:
            allowPrivilegeEscalation: false
            runAsNonRoot: true
            capabilities:
              drop:
                - ALL
          ports:
            - name: http
              containerPort: { { .Values.service.port } }
              protocol: TCP
          livenessProbe:
            httpGet:
              path: { { .Values.livenessProbe.path | default "/health" } }
              port: http
          readinessProbe:
            httpGet:
              path: { { .Values.readinessProbe.path | default "/ready" } }
              port: http
          resources: { { - toYaml .Values.resources | nindent 12 } }
```

**CRITICAL OpenShift Requirements:**

- ✅ `runAsNonRoot: true` - OpenShift restricted SCC requires this
- ✅ `allowPrivilegeEscalation: false` - No privilege escalation
- ✅ `capabilities.drop: [ALL]` - Drop all Linux capabilities
- ✅ No `hostPath`, `hostNetwork`, `hostPID`, `hostIPC`
- ✅ No hard-coded `runAsUser` or `fsGroup` (let OpenShift assign)
- ❌ Never set `privileged: true`
- ❌ Never mount host paths

### 2. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: { { include "app.fullname" . } }
  namespace: { { .Release.Namespace } }
  labels: { { - include "app.labels" . | nindent 4 } }
spec:
  type: { { .Values.service.type } }
  ports:
    - port: { { .Values.service.port } }
      targetPort: http
      protocol: TCP
      name: http
  selector: { { - include "app.selectorLabels" . | nindent 4 } }
```

### 3. ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: { { include "app.serviceAccountName" . } }
  namespace: { { .Release.Namespace } }
  labels: { { - include "app.labels" . | nindent 4 } }
```

### 4. Route (OpenShift Default)

**Use Route by default on OpenShift. It supports re-encrypt and passthrough TLS.**

```yaml
{{- if and .Values.route.enabled (eq .Values.platform "openshift") }}
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ .Release.Namespace }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  host: {{ include "app.hostname" . }}
  to:
    kind: Service
    name: {{ include "app.fullname" . }}
  port:
    targetPort: http
  tls:
    termination: {{ .Values.route.tls.termination | default "edge" }}
    insecureEdgeTerminationPolicy: Redirect
{{- end }}
```

### 5. Ingress (Optional, Kubernetes-compatible)

```yaml
{{- if and .Values.ingress.enabled (ne .Values.platform "openshift") }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ .Release.Namespace }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  rules:
  - host: {{ include "app.hostname" . }}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ include "app.fullname" . }}
            port:
              number: {{ .Values.service.port }}
{{- end }}
```

## Required values.yaml Structure

```yaml
# Cluster configuration (inherited from cluster values)
cluster:
  name: ""
  top_level_domain: ""
  platform: openshift # or kubernetes

# Application metadata
application:
  name: "My Application"
  group: "productivity"
  icon: "mdi:application"
  description: "Application description"

# Image configuration
image:
  repository: docker.io/myapp/myapp
  # renovate: datasource=docker depName=docker.io/myapp/myapp versioning=semver
  tag: "1.0.0"
  pullPolicy: IfNotPresent

# Replica count (topology-aware)
replicaCount: 1 # Override per topology

# Service configuration
service:
  type: ClusterIP
  port: 8080

# Route configuration (OpenShift)
route:
  enabled: true
  tls:
    termination: edge # edge, reencrypt, or passthrough

# Ingress configuration (Kubernetes)
ingress:
  enabled: false
  className: nginx

# Resources (adjust per topology)
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

# Persistence
persistence:
  enabled: false
  size: 1Gi
  storageClass: "" # Inherit from cluster default

# Security Context
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL

# Service Account
serviceAccount:
  create: true
  name: ""

# Monitoring (Prometheus)
monitoring:
  enabled: false
  path: /metrics
  port: 8080

# Health checks
livenessProbe:
  enabled: true
  path: /health
readinessProbe:
  enabled: true
  path: /ready

# HPA (optional)
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

# PDB (optional)
podDisruptionBudget:
  enabled: false
  minAvailable: 1

# Network Policy
networkPolicy:
  enabled: true
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: openshift-ingress
```

## Required \_helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "app.labels" -}}
helm.sh/chart: {{ include "app.chart" . }}
{{ include "app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate the hostname for routes/ingress
*/}}
{{- define "app.hostname" -}}
{{- printf "%s.apps.%s.%s" .Release.Name .Values.cluster.name .Values.cluster.top_level_domain }}
{{- end }}
```

## OpenShift-Specific Guardrails

### ❌ NEVER Include in App Charts

1. **SecurityContextConstraints (SCC)** - Platform responsibility

   ```yaml
   # ❌ BAD - Don't ship SCCs in app charts
   apiVersion: security.openshift.io/v1
   kind: SecurityContextConstraints
   ```

   **✅ INSTEAD:** Document required SCC in README:

   ```markdown
   ## Required Platform Configuration

   This application requires the `anyuid` SCC. Bind it in the platform chart:

   \`\`\`yaml

   # In platform chart

   oc adm policy add-scc-to-user anyuid -z myapp -n myapp-namespace
   \`\`\`
   ```

2. **ClusterRoles/ClusterRoleBindings** - Platform responsibility

   ```yaml
   # ❌ BAD - Cluster-scoped resources in app charts
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRole
   ```

   **✅ INSTEAD:** Use namespace-scoped Role/RoleBinding

3. **StorageClass** - Platform responsibility

   ```yaml
   # ❌ BAD - Don't define storage classes in apps
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   ```

   **✅ INSTEAD:** Reference cluster default or allow override

4. **Custom Resource Definitions (except app-specific)** - Usually platform

   ```yaml
   # ❌ BAD - Platform-wide CRDs in app charts
   # Example: cert-manager, external-secrets-operator CRDs
   ```

   **✅ ALLOWED:** App-specific CRDs in `/crds/` directory

### ✅ OpenShift Best Practices

1. **Use Route by Default**

   ```yaml
   # Default to Route on OpenShift
   route:
     enabled: true
     tls:
       termination: edge # or reencrypt, passthrough

   # Ingress as opt-in for Kubernetes
   ingress:
     enabled: false
   ```

2. **Assume Restricted SCC**

   ```yaml
   # All pods should work under restricted SCC
   securityContext:
     runAsNonRoot: true
     allowPrivilegeEscalation: false
     capabilities:
       drop:
         - ALL
   ```

3. **Use OpenShift-Specific Features**

   ```yaml
   # ConsoleLink for OpenShift Console integration
   apiVersion: console.openshift.io/v1
   kind: ConsoleLink
   metadata:
     name: { { include "app.fullname" . } }
   spec:
     href: { { include "app.hostname" . } }
     text: { { .Values.application.name } }
     location: ApplicationMenu
     applicationMenu:
       section: { { .Values.application.group } }
       imageURL: { { .Values.application.icon } }
   ```

4. **Health Checks for CRDs**

   If your app deploys CRDs, add Argo CD health checks:

   ```yaml
   # In GitOps repo (NOT in app chart)
   # roles/{cluster}/templates/argocd-resource-config.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: argocd-cm
     namespace: openshift-gitops
   data:
     resource.customizations.health.myapp.example.com_MyResource: |
       hs = {}
       if obj.status ~= nil then
         if obj.status.conditions ~= nil then
           for i, condition in ipairs(obj.status.conditions) do
             if condition.type == "Ready" and condition.status == "False" then
               hs.status = "Degraded"
               hs.message = condition.message
               return hs
             end
             if condition.type == "Ready" and condition.status == "True" then
               hs.status = "Healthy"
               hs.message = "Resource is ready"
               return hs
             end
           end
         end
       end
       hs.status = "Progressing"
       hs.message = "Waiting for resource"
       return hs
   ```

## Optional But Recommended

### 1. HorizontalPodAutoscaler

```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ .Release.Namespace }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "app.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
{{- end }}
```

### 2. PodDisruptionBudget

```yaml
{{- if .Values.podDisruptionBudget.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ .Release.Namespace }}
spec:
  minAvailable: {{ .Values.podDisruptionBudget.minAvailable }}
  selector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
{{- end }}
```

### 3. NetworkPolicy

```yaml
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ .Release.Namespace }}
spec:
  podSelector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
  policyTypes:
  - Ingress
  ingress:
  {{- toYaml .Values.networkPolicy.ingress | nindent 2 }}
{{- end }}
```

### 4. ServiceMonitor (Prometheus)

```yaml
{{- if .Values.monitoring.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "app.fullname" . }}
  namespace: {{ .Release.Namespace }}
spec:
  selector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
  endpoints:
  - port: http
    path: {{ .Values.monitoring.path }}
    interval: 30s
{{- end }}
```

### 5. Helm Tests

```yaml
# tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "app.fullname" . }}-test-connection"
  annotations:
    "helm.sh/hook": test
spec:
  containers:
  - name: wget
    image: busybox
    command: ['wget']
    args: ['{{ include "app.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

## values.schema.json (Recommended)

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["image", "service"],
  "properties": {
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": {
          "type": "string",
          "description": "Container image repository"
        },
        "tag": {
          "type": "string",
          "description": "Container image tag"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"],
          "default": "IfNotPresent"
        }
      }
    },
    "service": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["ClusterIP", "NodePort", "LoadBalancer"],
          "default": "ClusterIP"
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    }
  }
}
```

## Chart README Template

```markdown
# {App Name}

{Brief description}

## Prerequisites

- OpenShift 4.12+ or Kubernetes 1.24+
- Helm 3.8+
- {Any platform components required, e.g., External Secrets Operator}

## Required Platform Configuration

### SecurityContextConstraints (OpenShift)

This chart requires the **restricted** SCC (default). No additional SCCs needed.

### Storage

Requires a default StorageClass or specify `persistence.storageClass`.

## Installation

\`\`\`bash
helm install myapp ./charts/applications/{domain}/{app} \\
-f values-global.yaml \\
-f clusters/sets/values-home.yaml \\
-f clusters/individual-clusters/values-prod.yaml \\
-n myapp --create-namespace
\`\`\`

## Configuration

| Parameter             | Description            | Default                 |
| --------------------- | ---------------------- | ----------------------- |
| `image.repository`    | Container image        | `docker.io/myapp/myapp` |
| `image.tag`           | Image tag              | `1.0.0`                 |
| `replicaCount`        | Number of replicas     | `1`                     |
| `service.port`        | Service port           | `8080`                  |
| `route.enabled`       | Enable OpenShift Route | `true`                  |
| `persistence.enabled` | Enable persistence     | `false`                 |

## OpenShift Integration

- **Route:** Enabled by default for HTTPS access
- **ConsoleLink:** Adds link to OpenShift Console
- **SecurityContext:** Works under restricted SCC

## Kubernetes Compatibility

To use on vanilla Kubernetes:

\`\`\`yaml
cluster:
platform: kubernetes

route:
enabled: false

ingress:
enabled: true
className: nginx
\`\`\`

## Custom Resource Definitions

{List any CRDs in /crds/ directory and what they're for}

## Monitoring

Enable Prometheus monitoring:

\`\`\`yaml
monitoring:
enabled: true
path: /metrics
\`\`\`

## External Secrets

This chart integrates with External Secrets Operator:

\`\`\`yaml
externalSecrets:
enabled: true
secretStoreRef: cluster-secret-store
data: - secretKey: api-key
remoteRef:
key: myapp/api-key
\`\`\`
```

## Checklist for New Charts

Before submitting a new chart, ensure:

- [ ] Chart follows standard directory structure
- [ ] `Chart.yaml` has all required fields
- [ ] `values.yaml` follows standard structure
- [ ] `values.schema.json` exists and validates
- [ ] `README.md` documents all configuration options
- [ ] `_helpers.tpl` has standard helper functions
- [ ] Deployment uses restricted-compatible SecurityContext
- [ ] No cluster-scoped resources (ClusterRole, SCC, etc.)
- [ ] Route enabled by default, Ingress optional
- [ ] ServiceAccount created
- [ ] NetworkPolicy defined
- [ ] Helm test exists in `/tests/`
- [ ] CRDs (if any) are in `/crds/` directory
- [ ] Renovate comments on image tags
- [ ] ConsoleLink for OpenShift Console integration
- [ ] ExternalSecret integration (if secrets needed)
- [ ] No hard-coded UIDs or FSGroups
- [ ] Resources requests/limits defined
- [ ] Health probes configured
- [ ] Chart passes `helm lint`
- [ ] Chart passes standards audit (see below)

## Next Steps

See [CHART-AUDIT.md](./CHART-AUDIT.md) for the automated chart standards audit tool.
