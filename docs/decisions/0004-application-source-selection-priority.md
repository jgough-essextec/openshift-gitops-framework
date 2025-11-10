---
status: accepted
date: 2025-11-07
decision-makers: Repository Maintainers
consulted: Development Team, Operations Team
informed: All Contributors
---

# Application Source Selection Priority

## Context and Problem Statement

When adding new applications to the argo-apps repository, we need a consistent, documented approach for finding and selecting application sources (operators, Helm charts, container images). Without standardized guidance, contributors may:

- Choose suboptimal deployment methods (e.g., custom charts when operators exist)
- Use unofficial or unverified sources
- Select outdated or unmaintained packages
- Miss opportunities for lifecycle automation via operators
- Introduce security risks through untrusted sources

This ADR establishes the authoritative pattern for application source selection that must be followed when adding any new application.

## Decision Drivers

- **Operational Excellence**: Operators provide automated lifecycle management, reducing operational burden
- **Security**: Official and verified sources undergo security scanning and have established trust chains
- **Maintainability**: Well-maintained, officially supported components reduce long-term maintenance costs
- **OpenShift Compatibility**: Some sources are better tested with OpenShift than others
- **Community Support**: CNCF and official projects have stronger community support and documentation
- **Standardization**: Consistent approach across all applications simplifies troubleshooting and upgrades
- **Best Practices**: Kubernetes ecosystem best practices favor operator pattern for complex applications

## Considered Options

### Option 1: No Standardized Priority (Status Quo - Rejected)

Allow contributors to choose sources freely without guidance.

- ❌ Inconsistent deployment patterns
- ❌ Suboptimal choices (missing operators)
- ❌ Security risks from untrusted sources
- ❌ Higher maintenance burden

### Option 2: Helm-First Approach (Rejected)

Prioritize Helm charts over operators.

- ✅ Simpler initial deployment
- ❌ Manual lifecycle management
- ❌ No automated upgrades
- ❌ More operational overhead
- ❌ Against Kubernetes ecosystem trends

### Option 3: Operator-First with Source Priority (CHOSEN)

Establish clear priority: Operators > Helm > Custom, with source quality tiers.

- ✅ Automated lifecycle management
- ✅ Self-healing capabilities
- ✅ Security through verified sources
- ✅ Aligned with Kubernetes best practices
- ✅ Reduced operational overhead
- ⚠️ Steeper initial learning curve

## Decision Outcome

**Chosen option: "Operator-First with Source Priority"**

This decision establishes the following mandatory pattern for all new applications:

### 1. Deployment Method Priority

**Order of Preference:**

1. **Kubernetes Operator (Highest Priority)**

   - OLM (Operator Lifecycle Manager) operators preferred
   - Operator Helm charts acceptable
   - Direct operator installation (manifests) as fallback

2. **Helm Charts (Secondary)**

   - Only if no operator exists
   - Official charts from project maintainers preferred
   - Verified publishers on ArtifactHub

3. **Custom Deployments (Lowest Priority)**
   - Only if no operator or Helm chart exists
   - Must use official container images
   - Must follow chart standards

### 2. Source Quality Priority

**For All Deployment Methods:**

1. **Official** - Maintained by project authors
2. **Verified** - Verified publishers (Red Hat Certified, Certified Partners)
3. **CNCF** - Cloud Native Computing Foundation projects
4. **Community** - Well-maintained community projects

### 3. Repository Search Order

**When searching for applications:**

1. **[OperatorHub.io](https://operatorhub.io/)** - Kubernetes operators (OLM)

   - Priority: Red Hat Certified > Certified Partners > Community

2. **[ArtifactHub.io](https://artifacthub.io/)** - Helm charts and operators

   - Priority: Official > Verified Publisher > CNCF > Community

3. **[Quay.io](https://quay.io/)** - Container registry (Red Hat/OpenShift focused)

   - Priority: Official > Verified > Community

4. **[Docker Hub](https://hub.docker.com/)** - Container registry (general)
   - Priority: Official Images > Verified Publishers > Community

### Mandatory Workflow

**All contributors MUST:**

1. **Check for operator FIRST** - Search OperatorHub.io and ArtifactHub for operators
2. **Evaluate operator maturity** - Prefer Seamless Upgrades > Full Lifecycle > Basic Install
3. **If no operator** - Search for official Helm charts on ArtifactHub
4. **If no chart** - Use official container images from Quay.io or Docker Hub
5. **Document choice** - Record source, rationale, and alternatives considered in PR

### Consequences

**Good:**

- ✅ **Reduced Operational Overhead**: Operators automate lifecycle management, upgrades, and scaling
- ✅ **Improved Security**: Official and verified sources have security scanning and trust chains
- ✅ **Better Maintainability**: Well-supported sources reduce long-term maintenance burden
- ✅ **Consistency**: Standardized approach makes troubleshooting and knowledge transfer easier
- ✅ **Best Practices**: Aligned with Kubernetes ecosystem direction toward operators
- ✅ **Quality Assurance**: Source priority ensures high-quality, maintained components
- ✅ **OpenShift Native**: Preferred sources are better tested with OpenShift
- ✅ **Documentation**: Clear guidance reduces contributor confusion and mistakes

**Bad:**

- ⚠️ **Learning Curve**: Contributors must learn operator concepts and patterns
- ⚠️ **Search Time**: Requires checking multiple sources before proceeding
- ⚠️ **Complexity**: Operators can be more complex than simple Helm charts initially
- ⚠️ **Limited Options**: May need custom charts if no official sources exist

**Mitigations:**

- Comprehensive documentation in `docs/reference/PREFERRED-SOURCES.md`
- Quick reference guide: `docs/reference/APPLICATION-SOURCES-QUICK-REF.md`
- Step-by-step checklist: `docs/instructions/adding-an-application-checklist.md`
- Copilot instructions enforce pattern automatically
- Examples and templates provided for common scenarios

## Compliance

This ADR is **MANDATORY** for all new applications. The following mechanisms enforce compliance:

### Documentation

- Primary Guide: `docs/reference/PREFERRED-SOURCES.md` - Complete source selection guide
- Quick Reference: `docs/reference/APPLICATION-SOURCES-QUICK-REF.md` - One-page printable guide
- Application Checklist: `docs/instructions/adding-an-application-checklist.md` - Includes source verification
- Copilot Instructions: `.github/copilot-instructions.md` - AI assistant enforces pattern

### Verification

- **Pre-Commit**: Chart audit tool validates chart structure
- **Pull Request**: Reviewers verify source selection documented
- **Documentation**: PR description must include source rationale

### Exceptions

Deviations from this pattern must be:

1. Documented in `docs/CHART-EXCEPTIONS.md` with clear justification
2. Approved by maintainers
3. Include plan to migrate to preferred pattern when available

## Examples

### Example 1: EMQX MQTT Broker (Operator Available)

**Decision Flow:**

1. ✅ Search OperatorHub.io → Found EMQX Operator (Community)
2. ✅ Check ArtifactHub → Confirmed operator Helm chart available
3. ✅ Verify maturity → Full Lifecycle capabilities
4. ✅ Deploy operator to `charts/platform/emqx-operator/`
5. ✅ Create custom resource in `charts/applications/home-automation/emqx/`

**Rationale:** Official operator provides automated lifecycle management for MQTT broker.

### Example 2: Plex Media Server (No Operator)

**Decision Flow:**

1. ❌ Search OperatorHub.io → No operator found
2. ✅ Search ArtifactHub → Found community Helm chart
3. ⚠️ Not official, but well-maintained
4. ✅ Create custom chart based on community patterns
5. ✅ Use official Docker image: `docker.io/linuxserver/plex`

**Rationale:** No operator available. Used verified publisher image with custom chart following standards.

### Example 3: Glue Worker (Internal Application)

**Decision Flow:**

1. ❌ No operator (internal tool)
2. ❌ No Helm chart available
3. ✅ Build custom chart
4. ✅ Use official Python base image: `python:3.12-slim`
5. ✅ Build custom image from `src/glue-worker/`

**Rationale:** Internal application requires custom deployment. Based on official images.

## References

- [Preferred Sources Documentation](../reference/PREFERRED-SOURCES.md)
- [Application Sources Quick Reference](../reference/APPLICATION-SOURCES-QUICK-REF.md)
- [Adding Application Checklist](../instructions/adding-an-application-checklist.md)
- [Chart Standards](../CHART-STANDARDS.md)
- [Operator Maturity Model](https://operatorframework.io/operator-capabilities/)
- [OperatorHub.io](https://operatorhub.io/)
- [ArtifactHub.io](https://artifacthub.io/)

## Related Decisions

- [ADR-0001: Use OpenShift](./0001-use-openshift.md) - OpenShift compatibility influences source selection
- [ADR-0002: Validated Patterns Framework](./002-validated-patterns-framework-migration.md) - Framework structure supports operator pattern
- [ADR-0003: Topology Structure](./003-simplify-cluster-topology-structure.md) - Operators adapt to topology automatically

## Version History

- **2025-11-07**: Initial ADR - Established operator-first pattern with source priorities
