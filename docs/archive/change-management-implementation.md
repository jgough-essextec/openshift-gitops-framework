# Change Management and Consistency Implementation

## Summary

Created comprehensive change management processes and documentation to ensure consistency across the repository when making architectural or structural changes.

## Date

2025-01-06

## Changes Made

### 1. Created Change Management Guide

**File:** `docs/CHANGE-MANAGEMENT.md`

Comprehensive checklists for common change types:

- **Moving a Chart** - Files to update, documentation to sync, ADR considerations
- **Editing ApplicationSet Templates** - Role sync requirements, validation steps
- **Adding a New Application** - Complete checklist with cleanup script updates
- **Adding a New Application Domain** - Domain creation workflow
- **Modifying Platform Components** - Platform-level change considerations
- **Updating Topology Roles** - Topology-specific value changes

Each checklist includes:

- Files to create/update
- Documentation to maintain
- Verification steps
- ADR alignment checks
- Cleanup script maintenance

### 2. Enhanced Copilot Instructions

**File:** `.github/copilot-instructions.md`

Added new sections:

#### Change Management Protocol

- **Check ADRs FIRST** - Review decisions before changes
- **Follow or Update** - Align with ADRs or document exceptions
- **Use Change Checklists** - Reference CHANGE-MANAGEMENT.md
- **Update Cleanup Script** - Always add new resources
- **Maintain Consistency** - Update all related files

#### Enhanced Common Pitfalls

- Added "Not checking ADRs before making changes" as first pitfall
- Added "Not updating cleanup script" as critical requirement
- Added "Not following change management checklists"
- Added "Not syncing documentation"

#### Updated Application Addition Steps

- Added step 5: "Update cleanup script" with template code
- Renumbered subsequent steps
- Emphasized cleanup script maintenance

### 3. Verified Chart Exceptions Document

**File:** `docs/CHART-EXCEPTIONS.md` (already exists)

Confirmed this file exists for documenting standard deviations with:

- Exception template
- Documentation requirements
- Review process
- Current exceptions (CyberChef - anyuid SCC)

### 4. Key References Added

All documents now cross-reference:

- `docs/CHANGE-MANAGEMENT.md` - Change type checklists
- `docs/CHART-EXCEPTIONS.md` - Standard deviation tracking
- `docs/decisions/` - Architectural Decision Records
- `docs/CHART-STANDARDS.md` - Chart requirements
- `.github/copilot-instructions.md` - AI assistant guidance

## Workflow Integration

### Before Making Changes

1. **Review ADRs** in `docs/decisions/`
2. **Check Change Management Guide** for applicable checklist
3. **Review existing patterns** in codebase

### During Changes

1. **Follow checklist** from `docs/CHANGE-MANAGEMENT.md`
2. **Update all listed files** (code, docs, scripts)
3. **Document exceptions** in `docs/CHART-EXCEPTIONS.md` if needed

### After Changes

1. **Run verification scripts** (audit, app-inventory, template rendering)
2. **Update cleanup script** with new resources
3. **Sync documentation** across all affected files
4. **Test deployment** in appropriate cluster(s)

## Cleanup Script Maintenance

### Always Update When:

1. **Adding new applications** - Add namespace and application deletion
2. **Adding new operators** - Add CSV and subscription cleanup
3. **Adding new CRDs** - Add CR deletion before CRD removal
4. **Discovering stuck resources** - Add specific cleanup logic

### Template Added to Docs:

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

## ADR Compliance

### Decision Alignment

All changes must align with existing ADRs:

- **ADR 001:** Use OpenShift (Routes, SCC, OpenShift-native features)
- **ADR 002:** Validated Patterns Framework (Bootstrap → Roles → ApplicationSets)
- **ADR 003:** Topology Structure (SNO/Compact/Full roles)

### Exception Handling

When deviations occur:

1. Document in `docs/CHART-EXCEPTIONS.md`
2. Include technical justification
3. Note security/compatibility implications
4. Set review date

### Creating New ADRs

When patterns change:

1. Use `docs/decisions/template.md`
2. Document decision, context, consequences
3. Supersede old ADRs if applicable
4. Update copilot instructions

## Verification Commands

Added to change management guide:

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

## Benefits

1. **Consistency:** All changes follow same process
2. **Completeness:** Checklists ensure nothing missed
3. **Traceability:** ADRs document architectural decisions
4. **Maintainability:** Cleanup script keeps cluster clean
5. **Knowledge Transfer:** Documented processes for team
6. **AI Assistance:** Copilot instructions guide automated tools

## Related Documentation

- [Change Management Guide](docs/CHANGE-MANAGEMENT.md) - Complete checklists
- [Chart Exceptions](docs/CHART-EXCEPTIONS.md) - Standard deviations
- [Chart Standards](docs/CHART-STANDARDS.md) - Application requirements
- [Copilot Instructions](.github/copilot-instructions.md) - AI guidance
- [ADRs](docs/decisions/) - Architectural decisions

## Next Actions

When making changes:

1. ✅ Check ADRs first
2. ✅ Follow change management checklists
3. ✅ Update cleanup script
4. ✅ Document exceptions if needed
5. ✅ Sync all related documentation
6. ✅ Run verification scripts
7. ✅ Test in appropriate environment

---

**Remember:** Consistency through checklists prevents errors and maintains repository quality.
