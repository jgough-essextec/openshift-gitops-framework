# Topology-Aware Roles Design

## Overview

This document demonstrates how to use **roles** to encode **topology-specific defaults** (replica counts, PDB strategy, resource sizing) that automatically adapt applications based on cluster size.

## Problem Statement

Currently, we have topology values files (`values-sno.yaml`, `values-compact.yaml`, `values-full.yaml`) but the **roles** are identical duplicates. This misses an opportunity to make topology decisions automatic and declarative.

### Current Issues

1. **Manual Configuration**: Each app chart must manually check topology and set replicas
2. **Duplication**: Topology logic repeated across every app chart
3. **Error-Prone**: Easy to forget PDB configuration for compact/full topologies
4. **Roles Underutilized**: Role directories are just copies with no value-add

## Proposed Solution

**Encode topology defaults in role charts** that get automatically passed to all ApplicationSets and downstream applications.

### Architecture

```
Role Chart (roles/sno/)
  ↓ values.yaml contains topology defaults
  ↓
ApplicationSet Deployer (roles/sno/templates/media-applicationset.yaml)
  ↓ passes topology values to ApplicationSet chart
  ↓
ApplicationSet Chart (charts/applications/media/)
  ↓ passes topology values to each app
  ↓
Application Charts (charts/applications/media/plex/, sonarr/, etc.)
  ↓ uses topology.replicas.default, topology.pdb.enabled, etc.
```

## Implementation

### Step 1: Add Topology Defaults to Role values.yaml

**roles/sno/values.yaml:**

```yaml
topology:
  name: sno
  nodeCount: 1

  replicas:
    default: 1 # Most apps
    critical: 1 # Can't scale beyond 1 node

  pdb:
    enabled: false # No point on single node

  resources:
    small:
      requests: { memory: "128Mi", cpu: "50m" }
      limits: { memory: "256Mi", cpu: "200m" }
    medium:
      requests: { memory: "256Mi", cpu: "100m" }
      limits: { memory: "512Mi", cpu: "500m" }
    large:
      requests: { memory: "512Mi", cpu: "200m" }
      limits: { memory: "1Gi", cpu: "1000m" }
```

**roles/compact/values.yaml:**

```yaml
topology:
  name: compact
  nodeCount: 3

  replicas:
    default: 2 # HA with 2 replicas
    critical: 3 # Can use all nodes

  pdb:
    enabled: true
    minAvailable: 1 # Allow 1 disruption

  resources:
    small:
      requests: { memory: "256Mi", cpu: "100m" }
      limits: { memory: "512Mi", cpu: "500m" }
    medium:
      requests: { memory: "512Mi", cpu: "250m" }
      limits: { memory: "1Gi", cpu: "1000m" }
    large:
      requests: { memory: "1Gi", cpu: "500m" }
      limits: { memory: "2Gi", cpu: "2000m" }
```

**roles/full/values.yaml:**

```yaml
topology:
  name: full
  nodeCount: 6

  replicas:
    default: 3 # Standard HA
    critical: 5 # Can scale higher

  pdb:
    enabled: true
    minAvailable: 2 # Maintain 2 during disruptions

  resources:
    small:
      requests: { memory: "512Mi", cpu: "250m" }
      limits: { memory: "1Gi", cpu: "1000m" }
    medium:
      requests: { memory: "1Gi", cpu: "500m" }
      limits: { memory: "2Gi", cpu: "2000m" }
    large:
      requests: { memory: "2Gi", cpu: "1000m" }
      limits: { memory: "4Gi", cpu: "4000m" }
```

### Step 2: Update ApplicationSet Deployers to Pass Topology

**roles/sno/templates/media-applicationset.yaml:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {{ .Release.Name }}-media-applicationset
  namespace: openshift-gitops
spec:
  source:
    path: charts/applications/media
    helm:
      values: |
        spec:
{{ .Values.spec | toYaml | indent 10 }}
        topology:
{{ .Values.topology | toYaml | indent 10 }}
        config:
{{ .Values.config | toYaml | indent 10 }}
        clusterGroup:
{{ .Values.clusterGroup | toYaml | indent 10 }}
```

**Apply this change to ALL ApplicationSet deployers:**

- platform-applicationset.yaml
- media-applicationset.yaml
- ai-applicationset.yaml
- home-automation-applicationset.yaml
- productivity-applicationset.yaml
- infrastructure-applicationset.yaml

### Step 3: Update Application Charts to Use Topology Values

**Example: Plex StatefulSet**

**Before (Hardcoded):**

```yaml
# charts/applications/media/plex/templates/statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: { { .Release.Name } }
spec:
  replicas: 1 # ← HARDCODED
  # ... rest of spec
```

**After (Topology-Aware):**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: { { .Release.Name } }
spec:
  replicas: { { .Values.topology.replicas.default | default 1 } } # ← FROM TOPOLOGY
  # ... rest of spec
```

**Add PodDisruptionBudget Template:**

```yaml
# charts/applications/media/plex/templates/poddisruptionbudget.yaml
{{- if .Values.topology.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ .Release.Name }}
spec:
  minAvailable: {{ .Values.topology.pdb.minAvailable }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Release.Name }}
{{- end }}
```

**Update Resources:**

```yaml
# charts/applications/media/plex/templates/statefulset.yaml
containers:
  - name: main
    resources:
{{ .Values.topology.resources.large | toYaml | indent 6 }}
```

### Step 4: Override at Cluster Level When Needed

**values-test.yaml** (Override topology defaults):

```yaml
# Inherit topology from SNO role, but override specific apps
clusterGroup:
  applicationStacks:
    media:
      enabled: true
      apps:
        plex:
          # Override: Force 1 replica even if topology says otherwise
          replicas: 1
          # Override: Use smaller resources for test
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
```

## Benefits

### 1. **Automatic Scaling by Topology**

Deploy the same ApplicationSet to different topologies:

```bash
# SNO cluster - automatically gets 1 replica, no PDB
helm install sno ./roles/sno -f values-home.yaml -f values-sno.yaml

# Compact cluster - automatically gets 2 replicas, PDB with minAvailable=1
helm install hub ./roles/compact -f values-home.yaml -f values-hub.yaml

# Full cluster - automatically gets 3 replicas, PDB with minAvailable=2
helm install prod ./roles/full -f values-home.yaml -f values-prod.yaml
```

### 2. **DRY Principle**

Topology logic defined once in role, not repeated in every app chart.

### 3. **Safety**

PDBs automatically enabled for multi-node clusters, protecting against disruptions.

### 4. **Flexibility**

Cluster-specific values can still override topology defaults when needed.

### 5. **Clear Purpose for Roles**

Roles now have a **real function** beyond just being deployment wrappers.

## Migration Plan

### Phase 1: Add Topology Values to Roles ✅

- [x] Add `topology` section to `roles/sno/values.yaml`
- [x] Add `topology` section to `roles/compact/values.yaml`
- [x] Add `topology` section to `roles/full/values.yaml`

### Phase 2: Update ApplicationSet Deployers

- [ ] Update all ApplicationSet deployers to pass `topology` values
- [ ] Test Helm template rendering: `helm template sno ./roles/sno -f values-sno.yaml`

### Phase 3: Update Application Charts

- [ ] Add PodDisruptionBudget templates to app charts (conditional on `topology.pdb.enabled`)
- [ ] Replace hardcoded replicas with `{{ .Values.topology.replicas.default }}`
- [ ] Replace hardcoded resources with `{{ .Values.topology.resources.medium }}`

### Phase 4: Testing

- [ ] Deploy to test cluster (SNO topology) - verify 1 replica, no PDB
- [ ] Deploy hub cluster (compact topology) - verify 2 replicas, PDB created
- [ ] Verify cluster-specific overrides still work

## Examples: App Chart Updates

### Sonarr (Stateful Application)

```yaml
# charts/applications/media/sonarr/templates/statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
spec:
  replicas: {{ .Values.topology.replicas.default | default 1 }}
  template:
    spec:
      containers:
      - name: main
        resources:
{{ .Values.topology.resources.medium | toYaml | indent 10 }}
```

### OpenWebUI (Critical AI Service)

```yaml
# charts/applications/ai/open-webui/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: {{ .Values.topology.replicas.critical | default 1 }}  # ← Use "critical" tier
  template:
    spec:
      containers:
      - name: main
        resources:
{{ .Values.topology.resources.large | toYaml | indent 10 }}
```

### Gatus (Monitoring - High Availability)

```yaml
# charts/platform/gatus/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: { { .Values.topology.replicas.critical | default 1 } }
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: gatus
                topologyKey: kubernetes.io/hostname # ← Spread across nodes
```

## Advanced: HPA Integration

For applications that support HPA (compact/full topologies):

```yaml
# charts/applications/ai/litellm/templates/hpa.yaml
{{- if .Values.topology.hpa.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Release.Name }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Release.Name }}
  minReplicas: {{ .Values.topology.hpa.minReplicas | default .Values.topology.replicas.default }}
  maxReplicas: {{ .Values.topology.hpa.maxReplicas | default 10 }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ .Values.topology.hpa.targetCPUUtilization | default 70 }}
{{- end }}
```

## Validation

### Test Rendering

```bash
# SNO topology
helm template sno ./roles/sno -f values-global.yaml -f values-home.yaml -f values-sno.yaml \
  | grep -A5 "kind: StatefulSet" | grep replicas

# Expected: replicas: 1

# Compact topology
helm template hub ./roles/compact -f values-global.yaml -f values-home.yaml -f values-hub.yaml \
  | grep -A5 "kind: Deployment" | grep replicas

# Expected: replicas: 2 or 3

# Check PDB exists for compact
helm template hub ./roles/compact -f values-global.yaml -f values-home.yaml -f values-hub.yaml \
  | grep "kind: PodDisruptionBudget"

# Expected: PodDisruptionBudget resources found
```

## References

- [Kubernetes PodDisruptionBudget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [OpenShift Node Sizing](https://docs.openshift.com/container-platform/4.14/scalability_and_performance/planning-your-environment-according-to-object-maximums.html)
- ADR 003: Simplify Cluster Topology Structure
- Chart Standards: Resource Requirements and Replica Counts
