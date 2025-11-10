# AI Assistant Working Guide

Purpose: Provide just enough project-specific context so an AI agent can make correct, low‑risk changes immediately.

## 📚 Documentation Structure

**START HERE:** All documentation is indexed at `docs/INDEX.md`

**Key Documentation:**

- **Getting Started:** `docs/INDEX.md` → Getting Started section
- **Deployment Options:** `docs/deployment/DEPLOYMENT-OPTIONS.md` - Choose your deployment pattern
- **Configuration Guide:** `docs/CONFIGURATION-GUIDE.md` - Template vs user-specific files
- **Instructions Index:** `docs/instructions/INDEX.md` - Step-by-step workflows
- **Preferred Sources:** `docs/reference/PREFERRED-SOURCES.md` - Where to find charts/images/operators
- **Chart Standards:** `docs/CHART-STANDARDS.md` - Required standards (MUST follow)
- **Change Management:** `docs/CHANGE-MANAGEMENT.md` - Change checklists
- **Known Gaps:** `docs/KNOWN-GAPS.md` - Current limitations
- **TODO List:** `docs/TODO.md` - Planned improvements
- **Kubeconfig Management:** `docs/operations/KUBECONFIG-MANAGEMENT.md` - Multi-cluster credentials

**Note:** Instructions previously in `.github/instructions/` are now consolidated in `docs/instructions/`. Always reference `docs/` for user-facing documentation.

## Documentation Patterns (MUST Follow)

**CRITICAL:** When creating or updating documentation, follow the established three-tier hierarchy:

### Strategic → Tactical → Operational Hierarchy

1. **Strategic (ADRs)** - `docs/decisions/` - **WHY** decisions were made

   - Architectural Decision Records using MADR format
   - Document context, options considered, decision rationale, consequences
   - Create ADR for: platform changes, architectural patterns, security requirements, multi-cluster decisions
   - Example: ADR 008 (Multi-Cluster Strategy) explains WHY hub-and-spoke with ACM

2. **Tactical (Comprehensive Guides)** - `docs/` root - **WHAT** to do and WHEN

   - Comprehensive documentation explaining concepts and providing guidance
   - Include: DETAILED-OVERVIEW.md, VALUES-HIERARCHY.md, CHART-STANDARDS.md, CONFIGURATION-GUIDE.md
   - Deployment guides in `docs/deployment/` explain WHEN to use each pattern
   - Example: DEPLOYMENT-OPTIONS.md explains WHAT patterns exist and WHEN to choose each

3. **Operational (How-To Guides)** - `docs/instructions/`, `docs/operations/` - **HOW** to execute

   - Step-by-step instructions with exact commands
   - Checklists and workflows for specific tasks
   - Include: adding-application.md, ACM-GETTING-STARTED.md, KUBECONFIG-MANAGEMENT.md
   - Example: ACM-GETTING-STARTED.md shows HOW to set up ACM step-by-step

4. **Quick References** - `docs/reference/` - **Visual summaries** for rapid lookup
   - One-page printable references
   - Diagrams and visual guides
   - Include: ARCHITECTURE-QUICK-REF.md, APPLICATION-SOURCES-QUICK-REF.md
   - Example: ARCHITECTURE-QUICK-REF.md provides visual architecture overview in single page

### Cross-Reference Pattern

**Always link documents bidirectionally:**

```markdown
# Strategic ADR Example (docs/decisions/008-multi-cluster-management-strategy.md)

## Links

- **Pattern Selection:** [Deployment Options](../deployment/DEPLOYMENT-OPTIONS.md)
- **Operational Guide:** [ACM Getting Started](../ACM-GETTING-STARTED.md)

# Tactical Guide Example (docs/deployment/DEPLOYMENT-OPTIONS.md)

> **📋 Related Documentation:** See [ADR 008: Multi-Cluster Strategy](../decisions/008-multi-cluster-management-strategy.md) for rationale.

# Operational Guide Example (docs/ACM-GETTING-STARTED.md)

> **📋 Strategic Context:** See [ADR 008: Multi-Cluster Strategy](./decisions/008-multi-cluster-management-strategy.md) for the architectural decision.
```

### Documentation File Placement

- **Strategic decisions:** `docs/decisions/<number>-title.md`
- **Comprehensive guides:** `docs/<TOPIC>.md` (root level)
- **Deployment guides:** `docs/deployment/<pattern>-guide.md`
- **Instructions/workflows:** `docs/instructions/<task>.md`
- **Operations guides:** `docs/operations/<topic>.md`
- **Quick references:** `docs/reference/<TOPIC>-QUICK-REF.md`
- **Troubleshooting:** `docs/troubleshooting/<component>.md`
- **Archived content:** `docs/archive/<filename>.md`

### When Creating New Documentation

1. **Determine tier:** Strategic (why?), Tactical (what/when?), Operational (how?), or Quick Reference (visual)?
2. **Check existing coverage:** Search `docs/` before creating new file
3. **Add cross-references:** Link to related ADRs, guides, and quick-refs
4. **Update INDEX.md:** Add new doc to appropriate category in `docs/INDEX.md`
5. **Use consistent headers:**
   - Strategic ADR: Use MADR template from `docs/decisions/template.md`
   - Tactical Guide: Include "Related Documentation" section with ADR links
   - Operational Guide: Include "Strategic Context" banner linking to ADR
   - Quick Reference: Note "For detailed information, see [Comprehensive Guide]"

### Avoiding Duplication

**DO:**

- ✅ Brief mentions providing necessary context in specialized docs
- ✅ Quick references as intentional one-page summaries (printable)
- ✅ Multiple perspectives serving distinct audiences (user/operator/architect)
- ✅ Cross-references linking strategic → tactical → operational

**DON'T:**

- ❌ Copy-paste entire sections between documents
- ❌ Create new document without checking existing coverage
- ❌ Explain architecture/values hierarchy in detail outside primary docs
- ❌ Forget to add cross-references to related documentation

### Primary Sources (Single Source of Truth)

When topics are mentioned in multiple docs, these are the **authoritative** sources:

- **Architecture:** `docs/DETAILED-OVERVIEW.md` + `docs/reference/ARCHITECTURE-QUICK-REF.md`
- **Values Hierarchy:** `docs/VALUES-HIERARCHY.md` (ADR 005 for rationale)
- **Chart Standards:** `docs/CHART-STANDARDS.md` (ADR 006 for rationale)
- **Application Sources:** `docs/reference/PREFERRED-SOURCES.md` (ADR 004 for rationale)
- **Multi-Cluster:** ADR 008 (why), `docs/deployment/DEPLOYMENT-OPTIONS.md` (when), `docs/ACM-GETTING-STARTED.md` (how)
- **Configuration:** `docs/CONFIGURATION-GUIDE.md` (ADR 005 for rationale)

**Other docs should reference these, not duplicate them.**

## Big Picture

- This repo uses the **Red Hat Validated Patterns Framework** for GitOps: **bootstrap** (manual cluster Application) -> **roles** (Helm charts deploying ApplicationSets) -> **master ApplicationSets** (charts/platform/, charts/applications/\*/) -> **individual app charts**.
- The bootstrap process creates a single Argo CD `Application` named "cluster" pointing at `roles/<cluster-name>/` with values from `values-<cluster>.yaml` files in repo root.
- Each role (e.g., `prod`, `hub`, `test`) deploys **Applications that deploy ApplicationSets**:
  - `platform-applicationset.yaml` - Deploys the platform ApplicationSet chart
  - `ai-applicationset.yaml`, `media-applicationset.yaml`, etc. - Deploy application domain ApplicationSet charts
- ApplicationSets are defined once in `charts/platform/templates/applicationset.yaml` and `charts/applications/<domain>/templates/applicationset.yaml`, then deployed by all clusters
- Apps are enabled/disabled by adding/removing them from lists in `clusters/<subdirectory>/values-<cluster>.yaml` under `clusterGroup.applicationStacks.<domain>.apps`
- Configuration follows hierarchical values: `values-global.yaml` (pattern defaults) -> `clusters/<subdirectory>/values-<cluster>.yaml` (cluster-specific) -> individual chart values

## Key Directories

- `docs/operations/CLUSTER-BOOTSTRAP.md` – **Operational guide** (HOW to bootstrap). For architecture overview (WHY/WHAT), see `docs/DETAILED-OVERVIEW.md` and ADR 002
- `clusters/` (repo root) – **Values file organization directory** with subdirectories:
  - `individual-clusters/` – Per-cluster values (values-prod.yaml, values-hub.yaml, values-test.yaml)
  - `sets/` – Cluster set values (values-home.yaml, values-worklab.yaml, values-cloud.yaml)
  - `topologies/` – Topology defaults (values-compact.yaml, values-full.yaml)
- `values-global.yaml` (repo root) – Pattern-wide defaults inherited by all clusters
- `roles/<topology>/` – **Topology-specific Helm charts** (`prod`, `compact`, `full`). Each contains:
  - `Chart.yaml` – Defines the "cluster" chart
  - `values.yaml` – **Topology-specific defaults** (replica counts, PDB strategy, resource sizing)
  - `templates/*-applicationset.yaml` – Applications that deploy master ApplicationSet charts (platform, ai, media, home-automation, productivity, infrastructure)
  - **Note:** Templates are identical across roles (synced via `scripts/sync-role-templates.sh`); topology differences are in `values.yaml`
- `charts/platform/` – Master ApplicationSet chart for platform components. Contains `templates/applicationset.yaml` which generates Applications for ESO, certificates, VPA, Goldilocks, Gatus, storage providers (TrueNAS, Synology), MetalLB, GPU operators, ACM/MCE, Kasten, Keepalived, etc.
- `charts/applications/<domain>/` – Master ApplicationSet charts for each domain. Each contains `templates/applicationset.yaml`:
  - `ai/` – AI/ML applications (litellm, ollama, open-webui)
  - `media/` – Media management (plex, sonarr, radarr, overseerr, prowlarr, etc.)
  - `home-automation/` – IoT/smart home (home-assistant, node-red, emqx-operator, zwavejs2mqtt)
  - `productivity/` – Productivity tools (bookmarks, cyberchef, excalidraw, it-tools, startpunkt)
  - `infrastructure/` – Infrastructure apps (paperless suite, adsb, glue-worker)
- `charts/applications/<domain>/<app>/` – Individual application Helm charts (Deployments, Services, Routes, PVCs, etc.)
- `docs/instructions/` – **Step-by-step instructions** (adding apps, domains, checklists)
  - `adding-application.md` – Core workflow for adding applications
  - `adding-an-application-checklist.md` – **REQUIRED** checklist for new apps
  - `adding-a-new-domain.md` – Creating new application domains
  - `domains/<domain>.md` – Domain-specific instructions (ai, media, home-automation, etc.)
  - `INDEX.md` – Complete instructions index
- `docs/` – Documentation including troubleshooting guides, standards, and reference materials
  - `INDEX.md` – **START HERE** - Complete documentation index
  - `CONFIGURATION-GUIDE.md` – Template vs user-specific configuration files
  - `deployment/` – Deployment pattern guides and quick starts
  - `reference/PREFERRED-SOURCES.md` – Where to find application sources
  - `operations/KUBECONFIG-MANAGEMENT.md` – Managing cluster credentials
  - `TODO.md` and `KNOWN-GAPS.md` – Current status and limitations
- `scripts/` – Utility scripts for scaffolding charts, validating icons, VPA reporting, cluster cleanup

## Change Management Protocol

**CRITICAL:** Before making ANY architectural or structural changes:

1. **Check ADRs FIRST:** Review `docs/decisions/` for relevant Architectural Decision Records
   - **ADR Index:** `docs/decisions/INDEX.md` - Complete ADR catalog with summaries
   - **ADR 0000:** MADR Format - Use Markdown ADRs for all decisions
   - **ADR 0001:** Use OpenShift - Routes, SCC, OpenShift-native features (Platform)
   - **ADR 002:** Validated Patterns Framework - Bootstrap → Roles → ApplicationSets → Apps (Architecture)
   - **ADR 003:** Topology Structure - SNO/Compact/Full roles, topology-aware values (Infrastructure)
   - **ADR 004:** Application Source Selection - Operators > Helm > Custom, Official > Verified > CNCF (Applications)
   - **ADR 005:** Values Hierarchy Pattern - Global → Set → Topology → Cluster (Configuration)
   - **ADR 006:** Chart Standards & Security - Restricted SCC, namespace-scoped, Route-first (Standards)
   - **ADR 007:** Application Domain Organization - Functional domains (AI, Media, Home Automation, Productivity, Infrastructure) (Architecture)
   - **ADR 008:** Multi-Cluster Strategy - Hub-and-spoke with ACM, GitOps pull model (Multi-Cluster)
   - **ADR 009:** Use trash-guides Directory Structure - Standardize media storage layout (Media/Infrastructure)
   - **ADR 010:** Standardize Data Mounts for Media Containers - Consistent volume mounts across media stack (Media/Infrastructure)
2. **Follow or Update:** Changes must either:
   - Align with existing ADRs, OR
   - Document exception in `docs/CHART-EXCEPTIONS.md`, OR
   - Create new ADR to supersede old decision (use `docs/decisions/template.md`)
3. **Use Change Checklists:** Follow `docs/CHANGE-MANAGEMENT.md` for specific change types
4. **Update Cleanup Script:** Add new resources to `scripts/cluster-operations/cleanup-cluster.sh`
5. **Maintain Consistency:** Update all related documentation and files per checklist

**When moving charts or editing templates:** See `docs/CHANGE-MANAGEMENT.md` for complete checklists of files and documentation to update.

**When discovering cleanup issues:** Always add handling to cleanup script with proper ordering (CRs before CRDs, operators last).

## Core Patterns

1. **Validated Patterns Architecture:** Bootstrap Application deploys role chart → Role chart deploys ApplicationSet charts → ApplicationSet charts create Applications for each enabled app. Three-level hierarchy eliminates duplication while maintaining flexibility.
2. **Values Hierarchy:** Configuration follows Validated Patterns structure: `values-global.yaml` (pattern defaults) → `clusters/<subdirectory>/values-<cluster>.yaml` (cluster overrides). All config in `clusterGroup:` key including `platformComponents`, `applicationStacks`, `storage`, `network`, `certificates`, etc.
3. **App Enable/Disable:** Apps controlled by simple lists in `values-<cluster>.yaml`. Add/remove app names from `clusterGroup.applicationStacks.<domain>.apps` array. No ApplicationSet editing required - just update the values file.
4. **Master ApplicationSets:** Defined once in `charts/platform/templates/applicationset.yaml` and `charts/applications/<domain>/templates/applicationset.yaml`. Use Helm templating with `range` loops over app lists from values. All clusters use the same ApplicationSet definitions.
5. **Namespace Management:** ApplicationSets now use `managedNamespaceMetadata` to apply labels (e.g., `goldilocks.fairwinds.com/enabled: "true"`) to created namespaces. This is key for integration with operators like VPA/Goldilocks.
6. **App Chart Structure:** Each app chart should expose configurable: image (repository/tag), persistence (PVC size/class), route host (constructed from cluster top-level domain), resource requests, gatus monitoring config, and external secret references.
7. **CRD Management:** Charts that require Custom Resource Definitions (CRDs) must place them in a `crds/` directory at the chart root. Helm installs CRDs from `crds/` **before** any other resources, automatically handling dependency ordering. CRDs in `crds/` do NOT support Helm templating (no `{{ }}` syntax) and do NOT respect sync-wave annotations. Examples: MetalLB, operators, custom controllers.
8. **OpenShift Integrations:** Prefer Routes over Ingress, include `Route` TLS edge termination where practical, and use ConsoleLink / homepage integration patterns. Routes use the pattern: `<app-name>.apps.<cluster-name>.<top-level-domain>`.
9. **Version Updates:** Automated (Renovate) – keep image/tag parameters in `values.yaml` with renovate comments; avoid hardcoding in manifests.
10. **Sync Waves:** ApplicationSets use annotations like `argocd.argoproj.io/sync-wave` to control deployment order (0 for security/ESO, 50 for storage, 100 for apps, 200 for tweaks). CRDs are always installed first by Helm regardless of sync waves.
11. **Topology-Aware Roles:** Each role (`sno`, `compact`, `full`) defines topology-specific defaults in `values.yaml`:
    - **SNO (Single Node OpenShift)**: 1 replica, no PDBs, minimal resources (single node)
    - **Compact**: 2-3 replicas, PDB with minAvailable=1, moderate resources (3 nodes)
    - **Full**: 3+ replicas, PDB with minAvailable=2, full resources (6+ nodes)
    - Application charts use `{{ .Values.topology.replicas.default }}` for replica counts and conditional PDBs based on `{{ .Values.topology.pdb.enabled }}`
    - Use `scripts/sync-role-templates.sh` to keep role templates in sync (only templates/, not values.yaml)

## Helm Chart Standards

**CRITICAL:** All application charts MUST follow the standards defined in `docs/CHART-STANDARDS.md`.

### Key Standards:

- **Chart Structure:** Required files include `Chart.yaml`, `values.yaml`, `README.md`, `templates/_helpers.tpl`, `templates/NOTES.txt`
- **Security:** Charts MUST work under OpenShift restricted SCC (runAsNonRoot: true, allowPrivilegeEscalation: false, capabilities.drop: [ALL])
- **OpenShift Guardrails:** Apps MUST NOT include: SecurityContextConstraints, ClusterRole/ClusterRoleBinding, StorageClass, or platform-wide CRDs
- **Route by Default:** Use OpenShift Routes as primary ingress (Ingress as optional fallback)
- **CRDs Co-located:** App-specific CRDs go in `/crds/` directory (pure YAML, no Helm templating)
- **Namespace-Scoped:** All resources must be namespace-scoped (no cluster-level permissions)
- **Validation:** Run `python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>` to verify compliance

See full standards: `docs/CHART-STANDARDS.md`

## Adding a New Application (Agent Checklist)

**CRITICAL:** All new applications MUST follow ADR-004: Application Source Selection Priority

**Mandatory Pattern (from ADR-004):**

1. **Check for Kubernetes Operator FIRST** (Highest Priority)

   - Search [OperatorHub.io](https://operatorhub.io/) for OLM operators
   - Search [ArtifactHub.io](https://artifacthub.io/) for operator Helm charts
   - Priority: Red Hat Certified > Certified Partners > Community
   - If operator exists: Deploy to `charts/platform/` or `charts/applications/infrastructure/` first
   - Then create custom resource instance in application chart
   - Examples: EMQX Operator, cert-manager, MetalLB, Prometheus Operator

2. **If No Operator: Search for Helm Chart** (Secondary Priority)

   - Search [ArtifactHub.io](https://artifacthub.io/) for official/verified charts
   - Priority: Official > Verified Publisher > CNCF > Community
   - Verify OpenShift compatibility (Route support, SCC compliance)
   - Check recent updates (< 3 months ideal)

3. **If No Chart: Use Official Container Images** (Lowest Priority)

   - Search [Quay.io](https://quay.io/) (Red Hat/OpenShift focused)
   - Search [Docker Hub](https://hub.docker.com/) (general purpose)
   - Priority: Official Images > Verified Publishers > Community
   - Build custom chart following `docs/CHART-STANDARDS.md`

4. **You MUST:**
   - Document source selection rationale in PR description
   - Add to ALL cluster values files (commented by default)
   - Comply with `docs/CHART-STANDARDS.md`
   - Run audit tool before committing
   - Add to cleanup script

**Reference Documentation:**

- ADR-004: `docs/decisions/004-application-source-selection-priority.md`
- Detailed guide: `docs/reference/PREFERRED-SOURCES.md`
- Quick reference: `docs/reference/APPLICATION-SOURCES-QUICK-REF.md`
- Checklist: `docs/instructions/adding-an-application-checklist.md`
- Domain-specific: `docs/instructions/domains/<domain>.md`

### Quick Steps:

1. **Check for Kubernetes Operator:** Search for "[app-name] kubernetes operator" - if one exists, deploy the operator first as a platform/infrastructure chart before creating the application chart.

2. **Choose target domain:** Determine which functional group the app belongs to (`ai`, `media`, `home-automation`, `productivity`, `infrastructure`). The ApplicationSet for this domain is already defined in `charts/applications/<domain>/templates/applicationset.yaml`.

3. **Scaffold app Helm chart:** Create under `charts/applications/<domain>/<app>/` following `docs/CHART-STANDARDS.md` (use `scripts/chart-tools/scaffold-new-chart.sh`):

   - `Chart.yaml` – chart metadata with apiVersion v2
   - `values.yaml` – standard structure (image, service, route, resources, securityContext, etc.)
   - `README.md` – prerequisites, installation, configuration, OpenShift integration
   - `templates/_helpers.tpl` – required functions (app.name, app.fullname, app.labels, app.selectorLabels)
   - `templates/NOTES.txt` – post-installation instructions
   - `templates/deployment.yaml` or `statefulset.yaml` – with restricted SCC-compatible securityContext
   - `templates/service.yaml` – ClusterIP or LoadBalancer
   - `templates/serviceaccount.yaml` – dedicated service account
   - `templates/route.yaml` – OpenShift Route (edge/reencrypt/passthrough TLS)
   - `templates/ingress.yaml` (optional) – conditional on ingress.enabled
   - `crds/` (optional) – CustomResourceDefinitions required by the app (see CRD Management section below)

4. **Add app to cluster values files (COMMENTED BY DEFAULT):**

   **IMPORTANT: All values-\*.yaml files now contain complete application inventories!**

   All 38 available applications are already listed in every values file with descriptions:

   - Cluster values files (`clusters/individual-clusters/values-prod.yaml`, `clusters/individual-clusters/values-test.yaml`, `clusters/individual-clusters/values-hub.yaml`)
   - Topology values files (`clusters/topologies/values-compact.yaml`, `clusters/topologies/values-full.yaml`)
   - Cluster set values files (`clusters/sets/values-home.yaml`, `clusters/sets/values-worklab.yaml`, `clusters/sets/values-cloud.yaml`)
   - Global values file (`values-global.yaml`)

   **To add a NEW app:**

   a. Create the app chart in `charts/applications/<domain>/<app>/`
   b. Run `scripts/generate-app-list-template.py` to generate updated template
   c. Update ALL values files with the new app (commented by default)
   d. Use `scripts/verify-app-inventory.sh` to verify all files updated

   **To enable an EXISTING app:**

   Edit `values-<cluster>.yaml` and uncomment the app in `clusterGroup.applicationStacks.<domain>.apps`:

   ```yaml
   applicationStacks:
     ai:
       enabled: true
       apps:
         # - litellm          # AI proxy/router (commented = disabled)
         - ollama # Local LLM (uncommented = enabled)
         - open-webui # Web interface (enabled)
   ```

   **Default Pattern: All apps commented in ALL clusters unless explicitly enabled**

   - **Test:** All apps commented (uncomment specific apps for testing)
   - **Prod:** All apps commented (uncomment apps enabled for production)
   - **Hub:** All apps commented (management cluster, apps usually disabled)
   - **Compact/Full:** All apps commented (topology defaults)
   - **Cluster Sets:** Empty arrays (individual clusters define apps)

5. **Update cleanup script:** Add new app to `scripts/cluster-operations/cleanup-cluster.sh`:

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

   Add to the appropriate section: applications, operators, or tweaks. Maintain proper ordering (CRs before CRDs, operators last).

6. **Verify consistency:** Use the verification script to check all files:

   ```bash
   scripts/verify-app-inventory.sh
   ```

   This confirms all values files have the correct number of apps per domain.

7. **Test locally:** Run `helm template <cluster> ./roles/<cluster> -f values-<cluster>.yaml` to verify the ApplicationSet deployer and ApplicationSet generate correctly.

8. **Monitor deployment:** After commit, check `oc get application -n openshift-gitops` for ApplicationSet deployers, then `oc get applicationset -n openshift-gitops` for the ApplicationSets, then `oc get applications -A` for individual app Applications.

## Master ApplicationSets Structure

Master ApplicationSets are Helm charts that generate Applications for multiple components:

- **Platform ApplicationSet** (`charts/platform/`):

  - Contains `templates/applicationset.yaml` with Helm logic to iterate over `clusterGroup.platformComponents`
  - Generates Applications for ESO, certificates, VPA, Goldilocks, Gatus, storage (TrueNAS/Synology), MetalLB, GPU operators, ACM/MCE, Kasten, Keepalived, tweaks
  - Enabled/disabled via flags in `values-<cluster>.yaml` under `clusterGroup.platformComponents`

- **Application Domain ApplicationSets** (`charts/applications/<domain>/`):
  - Each contains `templates/applicationset.yaml` that ranges over `clusterGroup.applicationStacks.<domain>.apps`
  - Generates one Application per app in the list
  - Domains: `ai`, `media`, `home-automation`, `productivity`, `infrastructure`
  - `productivity.yaml` – Productivity tools
  - `delay-after-security.yaml`, `delay-after-storage.yaml` – Delay jobs to ensure dependencies are ready
  - `wait-for-eso-rbac.yaml` – RBAC resources for External Secrets Operator readiness checks
- To add a new ApplicationSet category, create a new template file following the existing pattern:
  - Use `{{ .Release.Name }}-<category>` as the ApplicationSet name
  - Define `generators.list.elements` with apps in that category
  - Set appropriate `sync-wave` annotation (0=security, 50=storage, 100=apps, 200=tweaks)
  - Include `managedNamespaceMetadata` with goldilocks label if VPA recommendations are desired
  - Pass `config` values to child Applications via `helm.valuesObject`
- **Important:** When modifying ApplicationSet templates, replicate changes across all cluster roles (`sno`, `hub`, `test`) to maintain consistency

## Naming & Conventions

- **Cluster/role names:** `prod` (production single node), `hub` (management cluster), `test` (testing cluster), `compact` (3-node topology), `full` (6+ node topology) – used as release name when deploying the role chart
- **ApplicationSet names:** `<release-name>-<category>` where release-name matches the cluster (e.g., `prod-ai`, `hub-media`, `test-base`)
  - Template uses: `{{ .Release.Name }}-<category>` to generate the correct name
- **Application names:** Match the app name exactly (`litellm`, `open-webui`, `plex`, etc.)
- **App chart directories:** `charts/applications/<domain>/<app>` where domain matches the functional category
- **Namespaces:** Automatically created per application, matching the application name
- **Routes:** Follow pattern `<app-name>.apps.<cluster-name>.<top-level-domain>`
- Avoid embedding environment names in resource names; rely on logical separation (namespaces, cluster names).

## Guardrails for Agents

- Do NOT introduce Kustomize overlays; stick to Helm + values.
- Preserve existing value keys; extend rather than rename to avoid breaking users.
- Before removing a chart or role, ensure a pruning path (role disabled) is clearly documented in PR description.
- Keep YAML indentation and style consistent with existing charts.

## Multi-Cluster Management

This workspace supports managing multiple OpenShift clusters simultaneously via cluster management functions (sourced from `.devcontainer/cluster-management.sh`).

### Available Clusters

- **prod** - Production single node OpenShift cluster
- **hub** - Hub/management cluster
- **test** - Testing cluster

### Cluster Context Commands

**CRITICAL: Always validate cluster context before troubleshooting or making changes.**

- **Switch clusters:** `hub`, `test`, or `prod` (shorthand functions)
- **Check current cluster:** `current` or `current-cluster`
- **Check all cluster status:** `status` or `cluster-status`
- **List kubeconfigs:** `clusters`

### AI Assistant Protocol

**Before executing any `oc` or `kubectl` commands:**

1. **Always check current cluster context first** using `current-cluster` or by checking `$KUBECONFIG`
2. **Confirm with user** if the target cluster is correct for the operation
3. **Warn user** if no cluster is selected or if cluster connectivity fails
4. **Suggest switching** if user's intent implies a different cluster (e.g., asking about "sno" apps while connected to "hub")

**When troubleshooting issues:**

- Run `current-cluster` to verify which cluster is active
- If operation fails with connectivity errors, run `cluster-status` to check all clusters
- Include cluster name in all diagnostic outputs: "Checking pods on **prod** cluster..."
- If user doesn't specify cluster, ask which cluster they want to investigate

**Example interaction pattern:**

```
User: "check if litellm is running"
Assistant: First, let me verify which cluster we're connected to...
[runs: current-cluster]
Assistant: We're currently on the **prod** cluster. Checking litellm status...
[runs: oc get pods -n litellm]
```

### Multi-Cluster Context Validation

When user requests operations that could affect multiple clusters:

- **Explicitly state** which cluster will be affected
- **Ask for confirmation** before making changes across clusters
- **Use cluster-specific commands** when iterating (e.g., save/restore `$KUBECONFIG`)

## Typical Commands (for human validation)

- **Render ApplicationSet for a cluster:** `helm template <cluster-name> ./roles/<cluster> -s templates/<category>.yaml`
- **Render all resources:** `helm template <cluster-name> ./roles/<cluster>`
- **Lint an app chart:** `helm lint charts/applications/<domain>/<app>`
- **Check ApplicationSets:** `oc get applicationset -n openshift-gitops`
- **Check Applications:** `oc get applications.argoproj.io -n openshift-gitops` (use `.argoproj.io` API, not `-A`)
- **Check app status:** `oc get pods -n <app-name>`

### CRITICAL: Argo CD API Resource Types

**ALWAYS use the full API group when working with Argo CD resources:**

- ✅ **CORRECT:** `oc get applications.argoproj.io -n openshift-gitops`
- ❌ **WRONG:** `oc get applications -A` (returns different/no resources)
- ✅ **CORRECT:** `oc get applicationsets.argoproj.io -n openshift-gitops`
- ✅ **CORRECT:** `oc get appprojects.argoproj.io -n openshift-gitops`
- ✅ **CORRECT:** `oc delete application.argoproj.io/<name> -n openshift-gitops`

**Why this matters:** OpenShift has multiple resource types named "Application":

- `applications.argoproj.io` - Argo CD applications (GitOps managed apps)
- `applications.app.k8s.io` - Kubernetes application metadata
- Using `oc get applications` without the API group may return the wrong type or nothing at all

**When cleaning up Argo CD:**

1. List: `oc get applications.argoproj.io -n openshift-gitops`
2. Remove finalizers: `oc patch application.argoproj.io/<name> -n openshift-gitops -p '{"metadata":{"finalizers":[]}}' --type=merge`
3. Delete: `oc delete applications.argoproj.io --all -n openshift-gitops`

## Chart Audit Tool

Use `scripts/audit/audit-chart-standards.py` to validate chart compliance:

- **Audit single chart:** `python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>`
- **Audit domain:** `python3 scripts/audit/audit-chart-standards.py --domain <domain>`
- **Audit all charts:** `python3 scripts/audit/audit-chart-standards.py --all`
- **Generate report:** Add `--markdown` for markdown output or `--json` for CI/CD integration

**Run audit BEFORE committing new charts or making changes to ensure compliance.**

**Documentation:** See `scripts/audit/README.md` and `scripts/README.md` for all available tools.

## When User Says… (Trigger Mapping)

- "add a chart" / "create a chart" / "add app <name>" → **FIRST check for operator**, then follow `docs/instructions/adding-an-application-checklist.md`, check domain-specific instructions in `docs/instructions/domains/<domain>.md`, validate with audit tool
- "add a domain" / "create a new ApplicationSet" / "new category" → follow `docs/instructions/adding-a-new-domain.md`
- "troubleshoot <app>" → **FIRST run `current-cluster` to validate context**, then check pod logs, route configuration, external secrets, PVC status
- "check <app>" / "is <app> running" → **FIRST run `current-cluster`**, then check pod status
- "switch to <cluster>" / "use <cluster>" → run appropriate cluster switch command (`hub`, `test`, or `prod`)
- "what cluster am I on" / "current cluster" → run `current-cluster`
- "show all clusters" / "cluster status" → run `cluster-status`
- "audit chart" / "validate chart" / "check compliance" → run audit tool on specified chart/domain/all
- "fix Home Assistant 400 error" or similar reverse proxy issues → check HTTP config for `use_x_forwarded_for` and `trusted_proxies`
- Any `oc` or `kubectl` command request → **FIRST verify cluster context with `current-cluster`**, confirm with user if needed

## CRD Management Best Practices

### When to Use the `crds/` Directory

Place CustomResourceDefinitions in `charts/applications/<domain>/<app>/crds/` when:

- The app is an operator (e.g., MetalLB, EMQX Operator, cert-manager)
- The app creates custom resources (e.g., `IPAddressPool`, `Certificate`, `ExternalSecret`)
- The app requires CRDs to be installed before any other resources

### CRD Directory Rules

**CRITICAL:** CRDs in the `crds/` directory have special behavior:

1. **Installation Timing:** Helm installs CRDs **before any other chart resources**, regardless of sync-wave annotations
2. **No Templating:** CRDs in `crds/` do NOT support Helm templating (`{{ }}` syntax will break)
3. **No Sync Waves:** `argocd.argoproj.io/sync-wave` annotations are ignored for CRDs in `crds/`
4. **Upgrade Limitations:** Helm does NOT automatically upgrade CRDs (manual deletion/recreation may be needed)

### CRD File Structure

```
charts/applications/<domain>/<app>/
├── Chart.yaml
├── values.yaml
├── crds/                          # ← CRDs go here
│   └── <resource>.crd.yaml        # Pure YAML, no Helm templates
└── templates/
    ├── deployment.yaml
    ├── custom-resource.yaml       # Uses the CRD defined above
    └── ...
```

### Example: MetalLB CRDs

```yaml
# charts/infrastructure/metallb/crds/metallb-crds.yaml
---
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: ipaddresspools.metallb.io
spec:
  group: metallb.io
  names:
    kind: IPAddressPool
    plural: ipaddresspools
  # ... (no Helm templating allowed here)
```

### Common CRD Sync Errors

- **"The Kubernetes API could not find <kind>"** → CRD not installed; check if it's in `crds/` or `templates/`
- **"no matches for kind"** → CRD missing or not installed yet; move to `crds/` directory
- **"Helm template error in crds/"** → Remove all `{{ }}` Helm syntax from CRD files

### When NOT to Use `crds/` Directory

- For simple apps without custom resources (Deployments, Services, Routes are standard Kubernetes resources)
- When you need to conditionally install CRDs based on Helm values (use templates/ instead, but ensure sync-wave=-5)
- For resources that use CRDs but aren't CRDs themselves (e.g., an `IPAddressPool` instance uses the CRD but isn't one)

## Common Pitfalls

- **Not checking ADRs before making changes:** ALWAYS review `docs/decisions/` before architectural changes. Deviations must be documented in `docs/CHART-EXCEPTIONS.md`.
- **Not updating cleanup script:** When adding new apps, operators, or discovering stuck resources, ALWAYS update `scripts/cluster-operations/cleanup-cluster.sh`.
- **Not following change management checklists:** See `docs/CHANGE-MANAGEMENT.md` for comprehensive checklists when moving charts, editing templates, or adding applications.
- **Not validating cluster context:** ALWAYS run `current-cluster` before executing `oc`/`kubectl` commands. Troubleshooting the wrong cluster wastes time and can cause confusion.
- **Forgetting to add app to ApplicationSet:** New apps won't be deployed unless added to the appropriate `generators.list.elements` in the ApplicationSet template.
- **Only updating one cluster role:** Changes to ApplicationSets need to be made in ALL cluster roles (sno, hub, test) unless the change is truly cluster-specific.
- **Hardcoding domain:** Always use `{{ .Values.cluster.top_level_domain }}` or similar value references instead of hardcoding domains.
- **Missing `spec.source.targetRevision`:** Ensure ApplicationSets use `targetRevision: HEAD` or specific branch/tag consistently.
- **ResourceVersion conflicts:** When ApplicationSets fail to sync with "metadata.resourceVersion: Invalid value: 0x0" errors, delete and recreate the ApplicationSet (Argo CD will regenerate child Applications).
- **Home Assistant reverse proxy errors:** OpenShift Routes require Home Assistant to trust proxy headers. Add HTTP config with `use_x_forwarded_for` and `trusted_proxies` for pod/service networks (10.128.0.0/14, 172.30.0.0/16).
- **Missing managedNamespaceMetadata:** New ApplicationSets should include `managedNamespaceMetadata.labels` for Goldilocks/VPA integration.
- **Incorrect sync-wave:** Security/ESO must be wave 0, storage wave 50, apps wave 100, tweaks wave 200.
- **CRDs in templates/ instead of crds/:** If an app requires CRDs, place them in `crds/` directory, not `templates/`. CRDs in templates/ may cause sync failures due to ordering issues.
- **Helm templating in CRDs:** CRD files in `crds/` directory must be pure YAML without any `{{ }}` Helm syntax.
- **Not syncing documentation:** When making structural changes, update all related docs: copilot instructions, ADRs, change management guide, standards, and quick references.

Keep responses concise and reference concrete file paths for edits.
