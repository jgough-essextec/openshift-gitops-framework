---
status: accepted
date: 2025-11-08
decision-makers: ["Platform Engineering Team"]
---

# Use Vertical Pod Autoscaler (VPA) with Goldilocks for Resource Right-Sizing

## Context and Problem Statement

Applications deployed to Kubernetes require resource requests and limits (CPU, memory), but determining the right values is challenging:

- **Too low:** Applications get OOMKilled or CPU throttled
- **Too high:** Wasted cluster resources, poor bin-packing
- **Static values:** Don't adapt to actual usage patterns
- **Trial and error:** Time-consuming to tune manually

The cluster needs an automated way to recommend and optionally apply right-sized resource requests based on actual usage.

## Decision Drivers

- **Resource Efficiency:** Maximize cluster utilization without overcommitting
- **Application Stability:** Prevent OOMKills and CPU starvation
- **Automation:** Reduce manual tuning effort
- **Observability:** Visibility into current vs. recommended resources
- **GitOps-Compatible:** Recommendations feed back into Helm chart values
- **OpenShift Support:** Must work with OpenShift restricted SCC

## Considered Options

1. **Vertical Pod Autoscaler (VPA)** - Kubernetes native resource recommendation/autoscaling
2. **Goldilocks** - VPA recommendation dashboard
3. **Manual Prometheus Queries** - DIY resource analysis
4. **Static Resource Templates** - Pre-defined resource tiers
5. **No Resource Management** - Let Kubernetes scheduler handle it

## Decision Outcome

Chosen option: **VPA + Goldilocks combination**, because:

- **VPA:** Provides actual resource recommendations based on historical usage
- **Goldilocks:** Adds visual dashboard for reviewing recommendations
- **Kubernetes-native:** VPA is part of Kubernetes Autoscaler project
- **OpenShift support:** Both work with OpenShift (VPA as platform component)
- **Recommendation mode:** Can run in advisory mode (doesn't modify pods)
- **Per-namespace:** Enabled via namespace label (`goldilocks.fairwinds.com/enabled: "true"`)

### Implementation Mode

**Recommendation-only mode** (not auto-scaling):

- VPA runs in "Off" mode (provides recommendations, doesn't modify pods)
- Goldilocks visualizes recommendations in dashboard
- Engineers review and apply recommendations to chart values
- GitOps workflow: Recommendations → values.yaml → PR → deploy

### Consequences

#### Good

- Data-driven resource requests based on actual usage
- Visual dashboard shows current vs. recommended resources
- Helps identify over-provisioned applications
- Prevents under-provisioning that causes instability
- Works across all namespaces with goldilocks label
- Recommendations inform capacity planning

#### Bad

- Additional operators to manage (VPA, Goldilocks)
- VPA requires metrics-server (already available in OpenShift)
- Recommendations are advisory only (manual application required)
- Need to monitor VPA itself

#### Neutral

- VPA recommendations updated every 24 hours by default
- Goldilocks requires namespace label to enable
- Dashboard access via OpenShift Route

## Implementation

### Platform Components

Both deployed as platform components:

1. **VPA Operator** (`charts/platform/vertical-pod-autoscaler/`):

   - OpenShift certified operator
   - Runs VPA recommender
   - Sync wave 0 (before applications)

2. **Goldilocks** (`charts/platform/goldilocks/`):
   - Deploys Goldilocks controller and dashboard
   - Automatically creates VPAs for labeled namespaces
   - Dashboard accessible via Route
   - Sync wave 100 (after applications)

### Namespace Configuration

ApplicationSets use `managedNamespaceMetadata` to label namespaces:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: prod-ai
spec:
  template:
    spec:
      syncPolicy:
        managedNamespaceMetadata:
          labels:
            goldilocks.fairwinds.com/enabled: "true"
```

### Application Pattern

Applications expose resource requests in values.yaml:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Workflow

1. **Deploy application** with initial resource estimates
2. **VPA observes** actual resource usage over time
3. **Goldilocks creates VPA** for namespace (via label)
4. **Dashboard shows** current vs. recommended resources
5. **Engineer reviews** recommendations in Goldilocks UI
6. **Update values.yaml** with new resource requests
7. **Commit to Git** → Argo CD syncs → Application redeploys

## Resource Right-Sizing Strategy

### Initial Values

- **Unknown workloads:** Conservative estimates (256Mi memory, 100m CPU)
- **Known patterns:** Based on similar applications
- **Vendor recommendations:** If documented

### VPA Configuration

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  updatePolicy:
    updateMode: "Off" # Recommendation-only
```

### Review Cadence

- **Weekly:** Review Goldilocks dashboard
- **Monthly:** Bulk update resource requests based on recommendations
- **After major changes:** Check recommendations following deployments

## Links

- **VPA Documentation:** <https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler>
- **Goldilocks:** <https://github.com/FairwindsOps/goldilocks>
- **VPA Implementation:** `charts/platform/vertical-pod-autoscaler/`
- **Goldilocks Implementation:** `charts/platform/goldilocks/`
- **Reporting Script:** `scripts/reporting/vpa-goldilocks-reporter.py`
- **Related ADRs:**
  - [ADR-002: Validated Patterns Framework](0002-validated-patterns-framework-migration.md) - Platform layer
  - [ADR-006: Chart Standards](0006-chart-standards-and-security.md) - Resource requirements
