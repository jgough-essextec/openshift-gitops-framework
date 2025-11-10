---
status: "accepted"
date: 2025-11-07
decision-makers:
  - Roy Bales
consulted:
  - OpenShift Documentation
  - Kubernetes Security Best Practices
informed:
  - Development Team
---

# ADR 006: Chart Standards and Security Posture

## Context and Problem Statement

Application Helm charts need consistent standards to ensure:

1. **Security:** Charts must work under OpenShift's restricted Security Context Constraints (SCC)
2. **Portability:** Charts should work on vanilla Kubernetes AND OpenShift
3. **Maintainability:** Consistent structure makes charts easier to understand and troubleshoot
4. **Separation of Concerns:** Clear boundaries between application and platform responsibilities
5. **CRD Management:** Reliable handling of CustomResourceDefinitions without timing issues

Without clear standards, charts become inconsistent, fail security validation, and require cluster-admin privileges.

## Decision Drivers

- OpenShift restricted SCC is the default (no privilege escalation)
- Namespace-scoped resources only (no cluster-wide permissions in app charts)
- CRD lifecycle management (install before resources, upgrade challenges)
- Route-first for OpenShift, Ingress as optional fallback
- Consistent documentation and testing patterns
- Separation between application and platform concerns

## Considered Options

1. **No Standards** - Let each chart define its own structure
2. **Kubernetes-First** - Optimize for vanilla Kubernetes, OpenShift as afterthought
3. **OpenShift-First with K8s Compatibility** - Default to OpenShift patterns, support K8s (chosen)
4. **Strict Enforcement** - Reject any chart not meeting 100% compliance
5. **Gradual Adoption** - Allow exceptions documented in CHART-EXCEPTIONS.md

## Decision Outcome

Chosen option: **OpenShift-First with K8s Compatibility + Gradual Adoption**, because it provides the best balance of security, portability, and pragmatism.

### Core Principles

1. **Keep Charts Boring** - Use standard, well-understood patterns. No clever tricks.
2. **Portable** - Charts should work on vanilla Kubernetes AND OpenShift
3. **OpenShift-Aware** - Default to OpenShift conventions, make Kubernetes features optional
4. **Namespace-Scoped** - Apps should never require cluster-level permissions
5. **CRDs Co-located** - Application-specific CRDs belong in the app's chart `/crds/` directory
6. **Platform Separation** - Cluster-level resources (SCCs, ClusterRoles, storage classes) belong in platform charts

### Security Context Requirements

**ALL application charts MUST work under OpenShift restricted SCC:**

#### Pod Security Context

```yaml
securityContext:
  runAsNonRoot: true
  seccompProfile:
    type: RuntimeDefault
```

#### Container Security Context

```yaml
securityContext:
  allowPrivilegeEscalation: false
  runAsNonRoot: true
  capabilities:
    drop:
      - ALL
```

**FORBIDDEN:**

- ❌ `privileged: true`
- ❌ Hard-coded UIDs or FSGroups
- ❌ `hostPath`, `hostNetwork`, `hostPID`, `hostIPC`
- ❌ Any capability additions (only drops allowed)

### Namespace-Scoped Resources Only

**Application charts MAY include:**

- ✅ `Role` (namespace-scoped RBAC)
- ✅ `RoleBinding` (namespace-scoped RBAC)
- ✅ `ServiceAccount` (required for every app)
- ✅ `NetworkPolicy` (namespace-scoped network rules)
- ✅ Application-specific CRDs in `/crds/` directory

**Application charts MUST NOT include:**

- ❌ `SecurityContextConstraints` (platform responsibility)
- ❌ `ClusterRole` or `ClusterRoleBinding` (cluster-wide permissions)
- ❌ `StorageClass` (platform/infrastructure responsibility)
- ❌ Platform-wide CRDs (only app-specific CRDs allowed)
- ❌ `MutatingWebhookConfiguration` or `ValidatingWebhookConfiguration`

### CRD Management Pattern

**Placement:**

- Application-specific CRDs go in `charts/applications/<domain>/<app>/crds/`
- Platform-wide CRDs go in `charts/platform/<component>/crds/`

**Format:**

- Pure YAML only (no Helm templating `{{ }}` syntax)
- No sync-wave annotations (Helm installs CRDs first automatically)
- Filenames: `*.crd.yaml` or `<resource>.crd.yaml`

**Example Structure:**

```
charts/applications/home-automation/emqx-operator/
├── crds/
│   ├── emqx.crd.yaml
│   └── emqxbroker.crd.yaml
└── templates/
    └── emqx-instance.yaml  # Uses the CRDs
```

**Helm CRD Behavior:**

1. Helm installs all CRDs from `/crds/` directory FIRST
2. CRDs installed before any templates/ resources
3. CRDs do NOT support Helm templating
4. Helm does NOT automatically upgrade CRDs (manual deletion required)

### Route-First Ingress Pattern

**Default:** Use OpenShift Route as primary ingress method

```yaml
# templates/route.yaml (default, always enabled)
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: { { include "app.fullname" . } }
spec:
  host:
    {
      {
        .Values.route.host | default (printf "%s.apps.%s.%s" .Values.application.name .Values.cluster.name .Values.cluster.top_level_domain),
      },
    }
  to:
    kind: Service
    name: { { include "app.fullname" . } }
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

**Optional:** Kubernetes Ingress as conditional fallback

```yaml
# templates/ingress.yaml (optional, conditional)
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
...
{{- end }}
```

### Required Chart Structure

```
charts/applications/<domain>/<app>/
├── Chart.yaml                    # Required - Chart metadata
├── values.yaml                   # Required - Default values
├── values.schema.json            # Recommended - JSON schema validation
├── README.md                     # Required - Documentation
├── crds/                         # Optional - App-specific CRDs only
│   └── *.crd.yaml
├── templates/
│   ├── NOTES.txt                 # Required - Post-install instructions
│   ├── _helpers.tpl              # Required - Template helpers
│   ├── deployment.yaml           # Required - Workload
│   ├── service.yaml              # Required - Service
│   ├── serviceaccount.yaml       # Required - ServiceAccount
│   ├── route.yaml                # Required - OpenShift Route
│   ├── ingress.yaml              # Optional - K8s Ingress
│   ├── role.yaml                 # Optional - Namespace RBAC
│   ├── rolebinding.yaml          # Optional - Namespace RBAC
│   ├── externalsecret.yaml       # Recommended - ESO integration
│   └── ...                       # Other optional resources
└── tests/
    └── test-connection.yaml      # Recommended - Helm test
```

### Required Helper Functions

Every chart MUST include in `templates/_helpers.tpl`:

```yaml
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

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

{{- define "app.labels" -}}
helm.sh/chart: {{ include "app.chart" . }}
{{ include "app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Consequences

**Good:**

- ✅ Consistent security posture across all applications
- ✅ Charts work in restricted environments (OpenShift default)
- ✅ Clear separation of concerns (apps vs platform)
- ✅ CRD timing issues eliminated
- ✅ Predictable chart structure aids troubleshooting
- ✅ Route-first pattern works natively on OpenShift
- ✅ Namespace-scoped resources enable multi-tenancy

**Bad:**

- ❌ Some upstream charts require modification
- ❌ Restricted SCC limits certain application types
- ❌ CRDs in /crds/ cannot use Helm templating
- ❌ Additional work to maintain custom charts
- ❌ Route objects not available on vanilla Kubernetes

**Neutral:**

- 🔄 Exceptions documented in CHART-EXCEPTIONS.md
- 🔄 Audit tool enforces standards programmatically
- 🔄 Gradual adoption allows incremental compliance

### Confirmation

Chart standards are being followed if:

1. **Audit Tool Passes:**

   ```bash
   python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>
   # Target: 100% compliance
   ```

2. **Security Validation:**

   ```bash
   # Chart deploys without SCC modifications
   oc get scc restricted -o yaml  # Should be unchanged

   # No privileged pods
   oc get pods -A -o jsonpath='{range .items[?(@.spec.securityContext.privileged==true)]}{.metadata.name}{"\n"}{end}'
   # Should return empty
   ```

3. **Namespace Scope:**

   ```bash
   # No cluster roles from app charts
   oc get clusterrole | grep -E '(app-name)'
   # Should return empty
   ```

4. **CRD Installation:**
   ```bash
   # CRDs installed before application
   oc get crd | grep <app-specific-resource>
   # Should exist before app pods are running
   ```

## Pros and Cons of the Options

### No Standards

- Good: Maximum flexibility
- Good: Faster initial development
- Bad: Inconsistent security posture
- Bad: Charts break in restricted environments
- Bad: Difficult to troubleshoot
- Bad: No clear ownership boundaries

### Kubernetes-First

- Good: Works everywhere Kubernetes runs
- Good: Large ecosystem of compatible charts
- Bad: Doesn't leverage OpenShift features (Routes, SCC)
- Bad: Requires additional Ingress controller setup
- Bad: Misses OpenShift security integrations

### OpenShift-First with K8s Compatibility (Chosen)

- Good: Secure by default (restricted SCC)
- Good: Leverages OpenShift features
- Good: Still works on vanilla K8s (with conditionals)
- Good: Clear security boundaries
- Bad: Requires understanding both platforms
- Bad: Some upstream charts need modification

### Strict Enforcement (100% Compliance Required)

- Good: No exceptions, perfect compliance
- Good: Easy to enforce
- Bad: Would block useful applications
- Bad: Upstream charts often non-compliant
- Bad: Slows adoption significantly

### Gradual Adoption (With Documented Exceptions)

- Good: Allows pragmatic deployment of non-compliant apps
- Good: Provides migration path
- Good: Documents technical debt
- Bad: Reduces consistency
- Bad: Exceptions can become permanent

## Links

- **Implementation:** `docs/CHART-STANDARDS.md` - Complete standards documentation
- **Audit Tool:** `scripts/audit/audit-chart-standards.py` - Automated compliance checking
- **Exceptions:** `docs/CHART-EXCEPTIONS.md` - Documented non-compliant charts
- **Related ADRs:**
  - ADR 001: Use OpenShift (Routes, SCC)
  - ADR 004: Application Source Selection (prefer official charts)
- **OpenShift SCC Documentation:** https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html
- **Kubernetes Security Context:** https://kubernetes.io/docs/tasks/configure-pod-container/security-context/

## Notes

- **Helm CRD Limitation:** CRDs in `/crds/` cannot be templated or upgraded automatically
- **Route Requirement:** All web-accessible apps must include OpenShift Route
- **ServiceAccount Required:** Every app needs dedicated ServiceAccount (principle of least privilege)
- **Audit Before Commit:** Run audit tool before committing new charts
- **Documentation Standard:** README.md must include prerequisites, configuration, troubleshooting
