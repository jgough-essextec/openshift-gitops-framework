---
applyTo: "**"
---

# Adding a New Application - Complete Checklist

This checklist ensures new applications follow ADR-004 standards and are properly integrated across all clusters.

## Pre-Flight Checks

- [ ] Review ADR-004: `docs/decisions/004-application-source-selection-priority.md`
- [ ] Review chart standards: `docs/CHART-STANDARDS.md`
- [ ] Check domain-specific instructions: `docs/instructions/domains/<domain>.md`
- [ ] Verify application doesn't already exist in charts directory
- [ ] Confirm which ApplicationSet the app belongs to (ai, media, home-automation, productivity, infrastructure, etc.)

## Step 1: Application Source Selection (ADR-004 MANDATORY)

**CRITICAL: Follow operator-first pattern defined in ADR-004**

### 1.1 Check for Kubernetes Operator (HIGHEST PRIORITY)

- [ ] Search [OperatorHub.io](https://operatorhub.io/) for OLM operators
- [ ] Search [ArtifactHub.io](https://artifacthub.io/) for operator Helm charts
- [ ] Evaluate operator priority: Red Hat Certified > Certified Partners > Community
- [ ] If operator found:
  - [ ] Deploy operator to `charts/platform/` or `charts/applications/infrastructure/`
  - [ ] Create custom resource instance in application chart
  - [ ] Document operator source in PR description

### 1.2 If No Operator: Search for Helm Chart (SECONDARY PRIORITY)

- [ ] Search [ArtifactHub.io](https://artifacthub.io/) for official/verified charts
- [ ] Evaluate chart priority: Official > Verified Publisher > CNCF > Community
- [ ] Verify OpenShift compatibility:
  - [ ] Route support (not just Ingress)
  - [ ] Restricted SCC compliance (runAsNonRoot, no privileged)
- [ ] Check recent updates (< 3 months ideal)
- [ ] Document chart source and version in `Chart.yaml` dependencies

### 1.3 If No Chart: Use Official Container Images (LOWEST PRIORITY)

- [ ] Search [Quay.io](https://quay.io/) (Red Hat/OpenShift focused)
- [ ] Search [Docker Hub](https://hub.docker.com/) (general purpose)
- [ ] Evaluate image priority: Official > Verified Publisher > Community
- [ ] Check image freshness and security scanning
- [ ] Build custom chart following `docs/CHART-STANDARDS.md`
- [ ] Document image source in `values.yaml`

**📚 Reference Documentation:**

- **ADR-004:** `docs/decisions/004-application-source-selection-priority.md`
- **Detailed Guide:** `docs/reference/PREFERRED-SOURCES.md`
- **Quick Reference (Print/Bookmark):** `docs/reference/APPLICATION-SOURCES-QUICK-REF.md`

## Step 2: Create Chart Structure

### Option A: Use Scaffold Script (Recommended)

```bash
./scripts/chart-tools/scaffold-new-chart.sh
# Follow prompts to select domain and app name
# Script will create compliant chart structure
```

- [ ] Run scaffold script
- [ ] Verify all required files created
- [ ] Customize generated templates

### Option B: Manual Creation

Create directory: `charts/applications/<domain>/<app>/`

**Required Files:**

- [ ] `Chart.yaml` - Chart metadata (apiVersion: v2)
- [ ] `values.yaml` - Configuration with standard structure
- [ ] `README.md` - Documentation (prerequisites, installation, configuration)
- [ ] `templates/_helpers.tpl` - Required helper functions
- [ ] `templates/NOTES.txt` - Post-installation instructions
- [ ] `templates/deployment.yaml` or `templates/statefulset.yaml` - Main workload
- [ ] `templates/service.yaml` - Service definition
- [ ] `templates/serviceaccount.yaml` - Dedicated service account
- [ ] `templates/route.yaml` - OpenShift Route (default ingress method)

**Recommended Files:**

- [ ] `values.schema.json` - JSON schema for values validation
- [ ] `templates/ingress.yaml` - Optional Ingress (conditional on ingress.enabled)
- [ ] `templates/networkpolicy.yaml` - Network policies
- [ ] `templates/pvc.yaml` - Persistent storage (if app needs it)
- [ ] `templates/configmap.yaml` - Configuration data
- [ ] `templates/externalsecret.yaml` - External Secrets Operator integration
- [ ] `templates/consolelink.yaml` - OpenShift Console integration
- [ ] `templates/servicemonitor.yaml` - Prometheus monitoring
- [ ] `tests/test-connection.yaml` - Helm test

**Optional (if needed):**

- [ ] `crds/*.crd.yaml` - App-specific CRDs (pure YAML, no templating)

## Step 3: Chart Content Requirements

### Security Context (CRITICAL)

**ALL apps MUST work under OpenShift restricted SCC:**

- [ ] `runAsNonRoot: true` in pod securityContext
- [ ] `runAsNonRoot: true` in container securityContext
- [ ] `allowPrivilegeEscalation: false` in container securityContext
- [ ] `capabilities.drop: [ALL]` in container securityContext
- [ ] `seccompProfile.type: RuntimeDefault` in pod securityContext
- [ ] NO hard-coded UIDs or FSGroups
- [ ] NO privileged: true
- [ ] NO hostPath, hostNetwork, hostPID, hostIPC

### OpenShift Guardrails (FORBIDDEN in App Charts)

**Apps MUST NOT include:**

- [ ] NO `SecurityContextConstraints` (platform responsibility)
- [ ] NO `ClusterRole` or `ClusterRoleBinding` (namespace-scoped only)
- [ ] NO `StorageClass` (platform responsibility)
- [ ] NO platform-wide CRDs (only app-specific CRDs in /crds/)

### values.yaml Requirements

- [ ] `cluster` section with top_level_domain, name, admin_email, timezone
- [ ] `application` section with name, group, icon, description
- [ ] `pods.main.image` with repository and tag
- [ ] Renovate comment above image tag
- [ ] `service`, `route`, `resources`, `securityContext` sections

### Required Helper Functions (_helpers.tpl)

- [ ] `app.name` - Chart name
- [ ] `app.fullname` - Fully qualified name
- [ ] `app.labels` - Common labels
- [ ] `app.selectorLabels` - Selector labels

### README.md Requirements

- [ ] Prerequisites section
- [ ] Installation instructions
- [ ] Configuration parameters table
- [ ] OpenShift integration notes
- [ ] Kubernetes compatibility notes
- [ ] Troubleshooting section

## Step 4: Add to Values Files

**CRITICAL: Add to ALL cluster values files COMMENTED BY DEFAULT**

### Update ALL Values Files

- [ ] Edit `clusters/individual-clusters/values-prod.yaml`
- [ ] Edit `clusters/individual-clusters/values-test.yaml`
- [ ] Edit `clusters/individual-clusters/values-hub.yaml`
- [ ] Edit `clusters/topologies/values-compact.yaml`
- [ ] Edit `clusters/topologies/values-full.yaml`
- [ ] Edit `clusters/sets/values-home.yaml`
- [ ] Edit `clusters/sets/values-worklab.yaml`
- [ ] Edit `clusters/sets/values-cloud.yaml`
- [ ] Edit `values-global.yaml`

Add commented entry under `clusterGroup.applicationStacks.<domain>.apps`:

```yaml
applicationStacks:
  <domain>:
    enabled: true
    apps:
      # Existing apps...
      # - <app-name>          # Brief description of app
```

### Verify Consistency

Run verification script:

```bash
./scripts/verify-app-inventory.sh
```

- [ ] All values files contain the new app entry
- [ ] Entry is commented by default
- [ ] Alphabetical order maintained

### Enable App (Optional)

To enable immediately, uncomment in specific cluster values file:

```yaml
applicationStacks:
  <domain>:
    enabled: true
    apps:
      - <app-name>          # Brief description of app (ENABLED)
```

## Step 5: Validation

### Helm Validation

```bash
helm lint charts/applications/<domain>/<app>
helm template <app-name> charts/applications/<domain>/<app> --validate
```

- [ ] `helm lint` passes with no errors
- [ ] `helm template` generates valid YAML

### Chart Standards Audit

```bash
python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>
```

**Target: 100% compliance**

- [ ] All required files present
- [ ] Security context compliant
- [ ] No forbidden cluster-scoped resources
- [ ] Route configured by default
- [ ] README.md complete

### Render ApplicationSets

```bash
helm template prod ./roles/full -f clusters/individual-clusters/values-prod.yaml
helm template test ./roles/compact -f clusters/individual-clusters/values-test.yaml
```

- [ ] ApplicationSet templates render without errors
- [ ] Values passed correctly to app chart

## Step 6: Update Cleanup Script

Add app to `scripts/cluster-operations/cleanup-cluster.sh`:

```bash
# <app-name> cleanup
if oc get project <app-name> &>/dev/null; then
    echo "Cleaning up <app-name>..."
    # Delete custom resources first if any
    oc delete <custom-resource> --all -n <app-name> --wait=false 2>/dev/null || true
    # Delete Argo CD application
    oc delete application <app-name> -n openshift-gitops --wait=false
    # Delete namespace
    oc delete namespace <app-name> --wait=false
fi
```

- [ ] Added to cleanup script
- [ ] Proper ordering (CRs before CRDs, operators last)
- [ ] Custom resources handled if applicable

## Step 7: Testing (if enabling immediately)

### Pre-Deployment

- [ ] Verify cluster context: `current-cluster`
- [ ] Commit and push changes

### Deployment

```bash
git add charts/applications/<domain>/<app>/
git add clusters/*/values-*.yaml values-global.yaml
git add scripts/cluster-operations/cleanup-cluster.sh
git commit -m "feat(apps): add <app-name> to <domain> domain"
git push
```

### Post-Deployment Monitoring

- [ ] ApplicationSet deployer created: `oc get application <domain>-applicationset -n openshift-gitops`
- [ ] ApplicationSet created: `oc get applicationset.argoproj.io <release-name>-<domain> -n openshift-gitops`
- [ ] Application created: `oc get application.argoproj.io <app-name> -n openshift-gitops`
- [ ] Namespace created with goldilocks label: `oc get namespace <app-name> -o yaml | grep goldilocks`
- [ ] Pods running: `oc get pods -n <app-name>`
- [ ] Route accessible: `oc get route -n <app-name>`
- [ ] Check logs for errors: `oc logs -n <app-name> -l app.kubernetes.io/name=<app-name>`

## Step 8: Documentation

- [ ] Update domain-specific instructions if needed: `docs/instructions/domains/<domain>.md`
- [ ] Document any external dependencies
- [ ] Add to monitoring/backup configurations if applicable
- [ ] Update PR description with source selection rationale (ADR-004 requirement)

## Final Checklist

- [ ] Chart follows `docs/CHART-STANDARDS.md` (100% audit compliance)
- [ ] ADR-004 source selection pattern followed (operator-first)
- [ ] Added to ALL cluster values files (commented by default)
- [ ] Cross-cluster consistency verified (`verify-app-inventory.sh`)
- [ ] Added to cleanup script with proper ordering
- [ ] If deployed: Pods running, Route accessible
- [ ] Documentation complete (README.md, domain instructions)
- [ ] Source selection documented in PR description

## Common Mistakes to Avoid

- ❌ **Not following ADR-004** → Must check for operators FIRST
- ❌ **Only adding to one values file** → Must add to ALL 9 values files
- ❌ **Not commenting by default** → Apps should be commented unless explicitly enabled
- ❌ **SecurityContextConstraints in app chart** → Move to platform
- ❌ **Missing security context fields** → Chart will fail on OpenShift
- ❌ **Missing README.md** → Documentation required
- ❌ **CRDs in templates/** → App-specific CRDs go in /crds/
- ❌ **Skipping audit tool** → Always validate compliance
- ❌ **Not updating cleanup script** → Resource cleanup will fail

## Quick Reference Commands

```bash
# Create chart
./scripts/chart-tools/scaffold-new-chart.sh

# Validate chart
helm lint charts/applications/<domain>/<app>
python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>

# Verify cross-cluster
./scripts/verify-app-inventory.sh

# Test ApplicationSet rendering
helm template prod ./roles/full -f clusters/individual-clusters/values-prod.yaml

# Deploy
git commit -am "feat(apps): add <app-name>"
git push

# Monitor deployment
oc get application.argoproj.io <app-name> -n openshift-gitops -w
oc get pods -n <app-name> -w
```

## Domain Categories Reference

- **ai** - AI/ML applications (litellm, ollama, open-webui)
- **media** - Media management (plex, sonarr, radarr, overseerr, prowlarr, etc.)
- **home-automation** - IoT/Smart Home (home-assistant, node-red, emqx-operator, zwavejs2mqtt)
- **productivity** - Productivity tools (bookmarks, cyberchef, excalidraw, it-tools, startpunkt)
- **infrastructure** - Infrastructure apps (paperless suite, adsb, glue-worker)

## ADR-004 Quick Reference

**Priority Order:**

1. **Operators** (OLM preferred) → OperatorHub.io, ArtifactHub.io
2. **Helm Charts** (official preferred) → ArtifactHub.io
3. **Container Images** → Quay.io, Docker Hub

**Source Quality Tiers:**

- Tier 1: Official / Red Hat Certified
- Tier 2: Verified / Certified Partners
- Tier 3: CNCF / Graduated Projects
- Tier 4: Community / Unverified

**Full documentation:** `docs/decisions/004-application-source-selection-priority.md`
