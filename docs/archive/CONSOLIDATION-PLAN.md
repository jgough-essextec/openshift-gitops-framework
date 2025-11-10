# Documentation Consolidation and Cleanup Plan

**Date:** 2025-11-07
**Status:** Proposed

## Summary

Analysis of documentation identified several opportunities to archive completed work, consolidate overlapping content, and eliminate outdated files.

---

## 🗂️ Archive Candidates (Move to `docs/archive/`)

### ADR Implementation Status Files

**Reason:** These are completion markers for work already integrated into main ADRs.

| File                                                       | Reason to Archive                          | Replacement                      |
| ---------------------------------------------------------- | ------------------------------------------ | -------------------------------- |
| `docs/decisions/003-PHASE-1-COMPLETE.md`                   | Implementation complete, historical record | ADR 003 shows final state        |
| `docs/decisions/003-REVISION.md`                           | Revision notes during ADR development      | ADR 003 is now accurate          |
| `docs/decisions/TOPOLOGY-ROLES-IMPLEMENTATION-COMPLETE.md` | Implementation complete, work done         | ADR 003 documents final decision |

**Action:**

```bash
mv docs/decisions/003-PHASE-1-COMPLETE.md docs/archive/
mv docs/decisions/003-REVISION.md docs/archive/
mv docs/decisions/TOPOLOGY-ROLES-IMPLEMENTATION-COMPLETE.md docs/archive/
```

### Completed Recommendations

| File                                     | Reason to Archive                               | Replacement                                    |
| ---------------------------------------- | ----------------------------------------------- | ---------------------------------------------- |
| `docs/SIMPLIFICATION-RECOMMENDATIONS.md` | Recommendations implemented in ADR 003, ADR 005 | ADR 003 (Topology), ADR 005 (Values Hierarchy) |

**Action:**

```bash
mv docs/SIMPLIFICATION-RECOMMENDATIONS.md docs/archive/
```

**Update References:**

- Remove from `docs/INDEX.md`
- Remove from `docs/README.md`

---

## 📋 Consolidation Opportunities

### 1. ACM Documentation

**Current State:**

- `docs/ACM-GETTING-STARTED.md` (664 lines) - Comprehensive ACM guide
- `docs/deployment/DEPLOYMENT-OPTIONS.md` - References ACM deployment
- **NEW:** `docs/decisions/008-multi-cluster-management-strategy.md` - Formalizes ACM strategy

**Recommendation: PARTIAL CONSOLIDATION**

**Keep:**

- `docs/ACM-GETTING-STARTED.md` - Detailed operational guide (how to use ACM)
- `docs/decisions/008-multi-cluster-management-strategy.md` - Strategic decision (why ACM)

**Reason:** They serve different purposes:

- ADR 008: Decision rationale, alternatives, strategy
- ACM-GETTING-STARTED: Tactical guide, step-by-step procedures, troubleshooting

**Action:** Add cross-reference at top of ACM-GETTING-STARTED.md:

```markdown
> **Strategic Context:** See [ADR 008: Multi-Cluster Strategy](./decisions/008-multi-cluster-management-strategy.md) for the decision rationale behind using ACM.
```

### 2. Values Hierarchy Documentation

**Current State:**

- `docs/VALUES-HIERARCHY.md` (490 lines) - Detailed usage examples
- **NEW:** `docs/decisions/005-values-hierarchy-pattern.md` - Decision rationale
- `docs/CONFIGURATION-GUIDE.md` - Template vs config guidance

**Recommendation: KEEP ALL, ADD CROSS-REFERENCES**

**Reason:** Each serves distinct purpose:

- ADR 005: Decision rationale and architecture
- VALUES-HIERARCHY.md: Practical examples and deployment patterns
- CONFIGURATION-GUIDE.md: What to modify where

**Action:** Add cross-references:

```markdown
# VALUES-HIERARCHY.md (add at top)

> **Decision Background:** See [ADR 005: Values Hierarchy Pattern](./decisions/005-values-hierarchy-pattern.md) for the architectural decision.

# CONFIGURATION-GUIDE.md (add at top)

> **Architecture:** See [ADR 005: Values Hierarchy Pattern](./decisions/005-values-hierarchy-pattern.md) for the values hierarchy architecture.
```

### 3. Chart Standards Documentation

**Current State:**

- `docs/CHART-STANDARDS.md` (781 lines) - Comprehensive implementation guide
- **NEW:** `docs/decisions/006-chart-standards-and-security.md` - Decision rationale
- `docs/CHART-EXCEPTIONS.md` - Documented exceptions

**Recommendation: KEEP ALL, ADD CROSS-REFERENCES**

**Reason:**

- ADR 006: Decision rationale, alternatives considered
- CHART-STANDARDS.md: Complete implementation guide with examples
- CHART-EXCEPTIONS.md: Pragmatic exceptions tracking

**Action:** Add cross-reference at top of CHART-STANDARDS.md:

```markdown
> **Decision Background:** See [ADR 006: Chart Standards & Security](./decisions/006-chart-standards-and-security.md) for the architectural decision.
```

### 4. Decision Tree vs Deployment Options

**Current State:**

- `docs/DECISION-TREE.md` (430 lines) - Detailed decision flows
- `docs/deployment/DEPLOYMENT-OPTIONS.md` (388 lines) - Deployment patterns
- Significant overlap in cluster set/topology decision logic

**Recommendation: CONSOLIDATE INTO DEPLOYMENT-OPTIONS.md**

**Reason:**

- Both serve same purpose: Guide deployment decisions
- DEPLOYMENT-OPTIONS.md is better organized (pattern-based)
- DECISION-TREE.md has more detailed cluster set info but less actionable
- Deployment directory is more discoverable for new users

**Action:**

1. Extract unique content from DECISION-TREE.md (cluster set details)
2. Merge into DEPLOYMENT-OPTIONS.md sections
3. Archive DECISION-TREE.md
4. Update INDEX.md references

```bash
# After manual content merge
mv docs/DECISION-TREE.md docs/archive/
```

---

## 🔄 Rename Suggestions

### ADR Numbering Consistency

**Current State:** Mixed numbering scheme:

- `0000`, `0001` (4-digit)
- `0002`, `0003` (4-digit, with leading zeros)
- `002`, `003` (3-digit)
- `004`, `005`, `006`, `007`, `008` (3-digit)

**Recommendation: STANDARDIZE ON 3-DIGIT WITH LEADING ZEROS**

**Proposed Renames:**

```bash
# Keep as-is (already correct format)
0000-use-markdown-architectural-decision-records.md ✓
0001-use-openshift.md ✓

# Rename media-specific ADRs to consolidate
mv 0002-use-trash-guides-directory-structure.md 009-media-trash-guides-directory-structure.md
mv 0003-standardize-data-mounts-for-media-containers.md 010-media-data-mount-standardization.md

# Rename main framework ADR
mv 002-validated-patterns-framework-migration.md 002-validated-patterns-framework.md

# Rename topology ADR
mv 003-simplify-cluster-topology-structure.md 003-cluster-topology-structure.md
```

**Updated Sequence:**

- 0000: MADR Format (meta)
- 0001: Use OpenShift (platform)
- 002: Validated Patterns Framework (architecture)
- 003: Cluster Topology Structure (infrastructure)
- 004: Application Source Selection (applications)
- 005: Values Hierarchy Pattern (configuration)
- 006: Chart Standards & Security (standards)
- 007: Application Domain Organization (architecture)
- 008: Multi-Cluster Strategy (multi-cluster)
- 009: Media TRaSH Guides Structure (media-specific)
- 010: Media Data Mount Standardization (media-specific)

---

## 🗑️ Delete Candidates

### None Identified

All current documentation serves a purpose. No deletion recommended at this time.

---

## 📝 Action Plan

### Phase 1: Archive Completed Work (Low Risk)

```bash
# Move implementation status files to archive
mv docs/decisions/003-PHASE-1-COMPLETE.md docs/archive/
mv docs/decisions/003-REVISION.md docs/archive/
mv docs/decisions/TOPOLOGY-ROLES-IMPLEMENTATION-COMPLETE.md docs/archive/

# Move completed recommendations
mv docs/SIMPLIFICATION-RECOMMENDATIONS.md docs/archive/
```

**Update Documentation:**

- Remove from `docs/INDEX.md` "Decisions & Planning" section
- Remove from `docs/README.md`
- Update `docs/archive/README.md` to list new additions

### Phase 2: Add Cross-References (Low Risk)

Add cross-reference banners to:

- `docs/ACM-GETTING-STARTED.md` → ADR 008
- `docs/VALUES-HIERARCHY.md` → ADR 005
- `docs/CONFIGURATION-GUIDE.md` → ADR 005
- `docs/CHART-STANDARDS.md` → ADR 006

### Phase 3: Consolidate Decision Tree (Medium Risk)

1. Review unique content in DECISION-TREE.md
2. Merge cluster set details into DEPLOYMENT-OPTIONS.md
3. Archive DECISION-TREE.md
4. Update all cross-references

### Phase 4: Standardize ADR Numbering (Medium Risk)

1. Rename ADRs per plan above
2. Update INDEX.md
3. Update copilot-instructions.md
4. Update all cross-references in documentation
5. Test all links

---

## Impact Assessment

### Breaking Changes

**None.** All changes are documentation-only:

- Archives preserve historical content
- Renames update references programmatically
- Consolidations maintain all content

### Search Impact

Users searching for archived files will:

1. Find them in `docs/archive/`
2. Be redirected via updated cross-references
3. See deprecation notices where appropriate

### Maintenance Benefit

- **-4 files** from main docs/ directory (cleaner structure)
- **-3 ADR status files** from decisions/ (less noise)
- **Consistent ADR numbering** (easier to reference)
- **Better cross-references** (clearer relationships)

---

## Rollout

### Immediate (Phase 1 - Archive)

- Move 4 files to archive
- Update INDEX.md
- Low risk, high value

### Next (Phase 2 - Cross-refs)

- Add ADR cross-references
- Improves discoverability
- No breaking changes

### Later (Phase 3 & 4)

- Decision tree consolidation
- ADR renumbering
- Requires coordination and testing

---

## Questions for Review

1. **Archive SIMPLIFICATION-RECOMMENDATIONS.md?** - Work is done, recommendations implemented
2. **Consolidate DECISION-TREE.md?** - Overlaps with DEPLOYMENT-OPTIONS.md
3. **Standardize ADR numbering?** - Mixed 3/4 digit scheme
4. **Keep ACM-GETTING-STARTED.md separate?** - Serves different purpose than ADR 008

---

**Recommendation: Proceed with Phase 1 (Archive) immediately. Defer Phase 3 & 4 pending user feedback.**
