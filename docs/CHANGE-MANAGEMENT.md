# Change Management Guide

## Purpose

This document provides checklists for common changes to ensure consistency across the repository. Always follow this guide when making architectural or structural changes.

## Quick Reference

**Before ANY change:**

```bash
# 1. Check ADRs
ls docs/decisions/

# 2. Find applicable checklist (below)
# Choose: Moving Chart, Editing Templates, Adding App, Adding Domain

# 3. Review existing patterns
grep -r "similar-pattern" .
```

**Most Common Tasks:**

| Task          | Key Steps                                                                             | Tools                                                                                                                    |
| ------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Add App       | Check for operator → Create chart → Update values → **Update cleanup script** → Audit | `scripts/generate-app-list-template.py`<br>`scripts/verify-app-inventory.sh`<br>`scripts/audit/audit-chart-standards.py` |
| Move Chart    | Update chart → Update ApplicationSets → Update values → Search/replace paths          | `grep -r "old/path" .`<br>`scripts/sync-role-templates.sh`                                                               |
| Edit Template | Edit source → Sync roles → Verify diff → Test render                                  | `scripts/sync-role-templates.sh`<br>`helm template ...`                                                                  |

**Cleanup Script Template** (add when creating any new app):

```bash
# <app-name> cleanup
if oc get project <app-name> &>/dev/null; then
    echo "Cleaning up <app-name>..."
    oc delete <custom-resource> --all -n <app-name> --wait=false 2>/dev/null || true
    oc delete application <app-name> -n openshift-gitops --wait=false
    oc delete namespace <app-name> --wait=false
fi
```

## General Principles

1. **Check ADRs First** - Review relevant Architectural Decision Records before making changes
2. **Update Documentation** - Keep all documentation in sync with code changes
3. **Update Copilot Instructions** - Ensure AI assistants understand the new patterns
4. **Update Cleanup Script** - Add new resources to cleanup procedures
5. **Document Exceptions** - If deviating from standards, document in CHART-EXCEPTIONS.md

## Change Type Checklists

### Moving a Chart

When moving a chart from one location to another:

#### Files to Update

- [ ] Chart source files (`Chart.yaml`, templates, values, etc.)
- [ ] ApplicationSet templates that reference the chart
- [ ] All cluster values files (`values-*.yaml`) with new path
- [ ] Role templates in `roles/*/templates/`

#### Documentation to Update

- [ ] `.github/copilot-instructions.md` - Update chart location references
- [ ] `docs/CHART-STANDARDS.md` - If location affects standards
- [ ] `README.md` - Update any architecture diagrams or references
- [ ] Relevant ADRs (if architectural change)

#### Verification Steps

1. Search for old path references: `grep -r "old/path" .`
2. Verify ApplicationSets render correctly: `helm template <cluster> ./roles/<cluster>`
3. Check all values files mention new location
4. Run `scripts/verify-app-inventory.sh` if applicable

#### ADR Considerations

- Does this move align with ADR 002 (Validated Patterns)?
- Does this move align with ADR 003 (Topology Structure)?
- If not, document exception in `docs/CHART-EXCEPTIONS.md`

---

### Editing ApplicationSet Templates

When modifying ApplicationSet template files (e.g., `roles/*/templates/*-applicationset.yaml`):

#### Files to Update

- [ ] **Source role** (e.g., `roles/sno/templates/*-applicationset.yaml`)
- [ ] **All other roles** - Run `scripts/sync-role-templates.sh`
- [ ] `values-*.yaml` files if new parameters added

#### Documentation to Update

- [ ] `.github/copilot-instructions.md` - "Master ApplicationSets Structure" section
- [ ] `docs/VALUES-HIERARCHY.md` - If values structure changed
- [ ] Relevant ADRs if template pattern changed

#### Verification Steps

1. Run sync script: `scripts/sync-role-templates.sh`
2. Verify all roles identical: `diff roles/sno/templates/*.yaml roles/compact/templates/*.yaml`
3. Test template rendering: `helm template <cluster> ./roles/<cluster>`
4. Check sync-wave annotations are correct

#### ADR Considerations

- ADR 002: Validated Patterns Framework - templates must follow pattern
- ADR 003: Topology Roles - only `values.yaml` differs between roles
- Document any deviations in `docs/CHART-EXCEPTIONS.md`

---

### Adding a New Application

When adding a new application chart:

#### Files to Create

- [ ] Chart directory: `charts/applications/<domain>/<app>/`
- [ ] `Chart.yaml` with proper metadata
- [ ] `values.yaml` with standard structure
- [ ] `README.md` with installation instructions
- [ ] `templates/_helpers.tpl` with required functions
- [ ] `templates/NOTES.txt` with post-install instructions
- [ ] `templates/deployment.yaml` or `statefulset.yaml`
- [ ] `templates/service.yaml`
- [ ] `templates/serviceaccount.yaml`
- [ ] `templates/route.yaml` (OpenShift)
- [ ] `templates/poddisruptionbudget.yaml` (if multi-replica)
- [ ] `crds/` directory if app requires CRDs

#### Files to Update

- [ ] **All values files** - Add app to `applicationStacks.<domain>.apps` (commented by default)
  - `values-prod.yaml`
  - `values-test.yaml`
  - `values-hub.yaml`
  - `values-compact.yaml`
  - `values-full.yaml`
  - `values-home.yaml` (if applicable)
  - `values-worklab.yaml`
  - `values-cloud.yaml`
  - `values-global.yaml`
- [ ] `scripts/generate-app-list-template.py` - Add app description
- [ ] `scripts/cluster-operations/cleanup-cluster.sh` - Add cleanup logic for new app

#### Documentation to Update

- [ ] `.github/copilot-instructions.md` - Update app counts per domain
- [ ] `docs/APP-MANAGEMENT-QUICK-REF.md` - Add app to domain list
- [ ] Domain-specific docs: `.github/instructions/domains/<domain>.md`
- [ ] `docs/values-app-inventory-update.md` - Update total count

#### Verification Steps

1. Run chart audit: `python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>`
2. Verify app in all values files: `scripts/verify-app-inventory.sh`
3. Test Helm template: `helm template <cluster> ./roles/<cluster> -f values-<cluster>.yaml`
4. Check ApplicationSet generates correctly: `helm template <cluster> ./roles/<cluster> -s templates/<domain>-applicationset.yaml`

#### ADR Considerations

- ADR 001: Use OpenShift - Chart must use Routes, not Ingress by default
- ADR 003: Topology Structure - Chart must support `topology.replicas.*` values
- Follow `docs/CHART-STANDARDS.md` completely
- Document any standard violations in `docs/CHART-EXCEPTIONS.md`

#### Cleanup Script Updates

Add to `scripts/cluster-operations/cleanup-cluster.sh`:

```bash
# <app-name> cleanup
if oc get project <app-name> &>/dev/null; then
    echo "Cleaning up <app-name>..."
    oc delete application <app-name> -n openshift-gitops --wait=false
    oc delete namespace <app-name> --wait=false
fi
```

---

### Adding a New Application Domain

When creating a new application domain (e.g., `charts/applications/<new-domain>/`):

#### Files to Create

- [ ] Domain directory: `charts/applications/<new-domain>/`
- [ ] Domain Chart.yaml: `charts/applications/<new-domain>/Chart.yaml`
- [ ] Domain templates: `charts/applications/<new-domain>/templates/applicationset.yaml`
- [ ] Domain values: `charts/applications/<new-domain>/values.yaml`
- [ ] Domain README: `charts/applications/<new-domain>/README.md`
- [ ] ApplicationSet deployer in all roles: `roles/*/templates/<new-domain>-applicationset.yaml`

#### Files to Update

- [ ] **All values files** - Add new domain to `applicationStacks`
- [ ] `scripts/verify-app-inventory.sh` - Add domain to expected counts
- [ ] `scripts/generate-app-list-template.py` - Add domain metadata

#### Documentation to Update

- [ ] `.github/copilot-instructions.md` - Add domain to "Adding a New Application" section
- [ ] `.github/instructions/adding-a-new-domain.md` - Update if exists
- [ ] `docs/APP-MANAGEMENT-QUICK-REF.md` - Add domain to table
- [ ] Create `.github/instructions/domains/<new-domain>.md` with domain-specific guidance

#### Verification Steps

1. Sync role templates: `scripts/sync-role-templates.sh`
2. Verify all values files updated: `scripts/verify-app-inventory.sh`
3. Test ApplicationSet rendering: `helm template <cluster> ./roles/<cluster>`

#### ADR Considerations

- ADR 002: Validated Patterns - Follow ApplicationSet pattern
- ADR 003: Topology Roles - Domain must respect topology values
- Document reasoning for new domain in commit message or ADR

---

### Modifying Platform Components

When changing platform components (charts/platform/\*):

#### Files to Update

- [ ] Platform component chart files
- [ ] `roles/*/templates/platform-applicationset.yaml` if component list changed
- [ ] All `values-*.yaml` files if new component added to `platformComponents`

#### Documentation to Update

- [ ] `.github/copilot-instructions.md` - "Core Patterns" section
- [ ] `docs/VALUES-HIERARCHY.md` - If values structure changed

#### Verification Steps

1. Test platform ApplicationSet: `helm template <cluster> ./roles/<cluster> -s templates/platform-applicationset.yaml`
2. Verify sync-waves are correct (0=security, 50=storage, 100=apps, 200=tweaks)

#### ADR Considerations

- Platform components are foundational - changes require careful review
- Consider impact on all cluster types (SNO, compact, full)

---

### Updating Topology Roles

When modifying topology-specific values (roles/\*/values.yaml):

#### Files to Update

- [ ] **Specific role values**: `roles/<topology>/values.yaml`
- [ ] Do NOT sync templates - only values should differ between roles

#### Documentation to Update

- [ ] `.github/copilot-instructions.md` - "Core Patterns #11: Topology-Aware Roles"
- [ ] `docs/TOPOLOGY-ROLES-IMPLEMENTATION-COMPLETE.md` - If changing replica counts

#### Verification Steps

1. Verify templates remain identical: `diff roles/sno/templates/*.yaml roles/compact/templates/*.yaml`
2. Test values override correctly: `helm template <cluster> ./roles/<cluster>`

#### ADR Considerations

- ADR 003: Topology Structure - Only `values.yaml` should differ between roles
- Templates MUST remain identical across roles

---

## Exception Documentation

When deviating from standards or ADRs, document in `docs/CHART-EXCEPTIONS.md`:

```markdown
## Chart: <app-name>

**Exception:** <Brief description>

**Reason:** <Why this exception is necessary>

**Standard Violated:** <Reference to CHART-STANDARDS.md section or ADR>

**Approved By:** <Name/Date>

**Alternative Approach:** <What was done instead>

**Impact:** <Security/compatibility/maintenance implications>
```

---

## Cleanup Script Maintenance

Always update `scripts/cluster-operations/cleanup-cluster.sh` when:

1. **Adding new applications** - Add namespace and application deletion
2. **Adding new operators** - Add CSV and subscription cleanup
3. **Adding new CRDs** - Add CR deletion before CRD removal
4. **Discovering new stuck resources** - Add specific cleanup logic

Template for new app cleanup:

```bash
# <App Name> cleanup
if oc get project <app-namespace> &>/dev/null; then
    echo "Cleaning up <app-name>..."

    # Delete custom resources first (if any)
    oc delete <custom-resource> --all -n <app-namespace> --wait=false

    # Delete Argo CD application
    oc delete application <app-name> -n openshift-gitops --wait=false

    # Delete namespace
    oc delete namespace <app-namespace> --wait=false
fi
```

---

## ADR Review Checklist

Before making architectural changes:

1. [ ] Read relevant ADRs in `docs/decisions/`
2. [ ] Verify change aligns with existing decisions
3. [ ] If misalignment:
   - [ ] Document exception in `docs/CHART-EXCEPTIONS.md`, OR
   - [ ] Create new ADR to supersede old decision
4. [ ] Update copilot instructions with new pattern
5. [ ] Update this change management guide if new pattern emerges

---

## Key References

- **ADR 001:** Use OpenShift (`docs/decisions/0001-use-openshift.md`)
- **ADR 002:** Validated Patterns Framework (`docs/decisions/002-validated-patterns-framework-migration.md`)
- **ADR 003:** Topology Structure (`docs/decisions/003-simplify-cluster-topology-structure.md`)
- **Chart Standards:** `docs/CHART-STANDARDS.md`
- **Chart Exceptions:** `docs/CHART-EXCEPTIONS.md`
- **Values Hierarchy:** `docs/VALUES-HIERARCHY.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`

---

## Quick Validation Commands

```bash
# Verify app inventory consistency
scripts/verify-app-inventory.sh

# Audit chart compliance
python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>

# Sync role templates
scripts/sync-role-templates.sh

# Test Helm rendering
helm template <cluster> ./roles/<cluster> -f values-<cluster>.yaml

# Check for old references after move
grep -r "old/path/pattern" .

# Verify templates identical across roles
for file in roles/sno/templates/*.yaml; do
  filename=$(basename "$file")
  diff "$file" "roles/compact/templates/$filename" || echo "MISMATCH: $filename"
done
```

---

**Remember:** Consistency is key. When in doubt, check the ADRs and follow the patterns established in existing code.
