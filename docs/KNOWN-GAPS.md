# Known Gaps & Limitations

Identified limitations, missing features, and areas requiring improvement in the argo-apps repository.

**Last Updated:** 2025-11-07

---

## 🏗️ Architecture & Design

### Template vs Configuration Separation

**Status:** ⚠️ Needs Improvement

**Problem:**

- No clear delineation between template/framework files and user-specific configurations
- Difficult for users to identify what should be customized vs. left as-is
- Risk of users modifying framework files inadvertently

**Impact:**

- Confusion during initial setup
- Potential framework breakage from incorrect modifications
- Difficult to update framework without affecting user configs

**Proposed Solution:**

- Create `docs/CONFIGURATION-GUIDE.md` documenting:
  - Template files (DO NOT MODIFY): `roles/*/templates/`, `values-global.yaml`, base charts
  - Configuration files (CUSTOMIZE): `clusters/*/values-*.yaml`, app-specific values
  - Optional files (EXTEND): Domain-specific charts, custom applications
- Add README files in key directories explaining their purpose
- Consider directory restructuring: `framework/` vs. `config/` vs. `custom/`

**Workaround:**

- Follow documentation carefully
- Refer to `.github/copilot-instructions.md` for guidance
- Use provided examples as templates

**Related:**

- [TODO - Configuration Guide](./TODO.md#documentation-improvements)
- [Values Hierarchy](./VALUES-HIERARCHY.md)

---

### Documentation Organization

**Status:** ⚠️ In Progress

**Problem:**

- Instructions split between `.github/instructions/` and `docs/`
- No single entry point for all documentation
- Difficult to find related documentation
- Copilot instructions reference files that may move

**Impact:**

- Users struggle to find relevant documentation
- Maintainers need to update multiple locations
- Inconsistent documentation structure

**Proposed Solution:**

- Consolidate all instructions under `docs/instructions/`
- Create `docs/INDEX.md` with comprehensive navigation
- Update `.github/copilot-instructions.md` to reference consolidated locations
- Ensure all docs link to the index

**Status:**

- ✅ `docs/INDEX.md` created
- 🚧 Moving `.github/instructions/` to `docs/instructions/` (in progress)
- ⏳ Updating copilot instructions (pending)

**Related:**

- [TODO - Consolidate Instructions](./TODO.md#documentation-improvements)
- [Documentation Index](./INDEX.md)

---

## 🐳 Applications

### Applications Requiring Custom Images

**Status:** ⚠️ Identified, Build Automation Needed

**Problem:**
Several applications require custom-built images but lack automated build pipelines:

1. **Glue Worker** (`src/glue-worker/`)

   - Purpose: Custom data processing application
   - Base: Python 3.12
   - Needs: GitHub Actions or Tekton pipeline
   - Current: Manual builds

2. **Paperless GPT** (`src/paperless-gpt/`)
   - Purpose: AI-enhanced document processing
   - Base: Python with AI libraries
   - Needs: Multi-stage build for size optimization
   - Current: Manual builds

**Impact:**

- No automated version updates
- Manual build process error-prone
- Difficult to maintain consistency
- No security scanning in pipeline

**Proposed Solution:**

- Create GitHub Actions workflows in `.github/workflows/`:
  - `build-glue-worker.yaml`
  - `build-paperless-gpt.yaml`
- Use multi-stage builds for optimization
- Integrate security scanning (Trivy, Snyk)
- Push to Quay.io or GitHub Container Registry
- Tag with Git SHA and semantic version
- Trigger on src/ directory changes

**Workaround:**

- Build images manually
- Push to personal registry
- Update chart values to use custom image location

**Related:**

- [TODO - Image Build Automation](./TODO.md#application-management)

---

### Incomplete Application Coverage

**Status:** ⚠️ Ongoing

**Problem:**
Not all application domains have equal coverage:

**Well-Covered Domains:**

- ✅ AI Stack: LiteLLM, Ollama, Open WebUI
- ✅ Media: Plex, Sonarr, Radarr, Overseerr, Prowlarr
- ✅ Platform: ESO, VPA, Goldilocks, Gatus, MetalLB

**Under-Developed Domains:**

- ⚠️ Home Automation: Limited apps, needs Node-RED, EMQX examples
- ⚠️ Productivity: Basic apps, could expand
- ⚠️ Infrastructure: Needs more examples

**Missing Domains:**

- ❌ Developer Tools: No CI/CD, source control, or artifact management
- ❌ Observability: No centralized logging, tracing, or metrics
- ❌ Security: No vulnerability scanning, policy enforcement tools

**Impact:**

- Users may need to create charts from scratch
- Inconsistent patterns across domains
- Limited examples for new contributors

**Proposed Solution:**

- Add high-demand applications per domain
- Create domain-specific README files with application lists
- Prioritize based on user requests and common use cases
- Document application roadmap

**Related:**

- [Preferred Sources](./reference/PREFERRED-SOURCES.md)
- [Adding Application Checklist](./instructions/adding-an-application-checklist.md)

---

## 🔧 Operations

### Kubeconfig Management

**Status:** ⚠️ Undocumented

**Problem:**

- No standardized approach for managing multiple kubeconfigs
- Cluster context switching not well documented
- Devcontainer provides functions but lacks written guidance
- No guidance on secure storage or rotation

**Impact:**

- Users may struggle with multi-cluster operations
- Risk of executing commands on wrong cluster
- Potential security issues with kubeconfig storage

**Proposed Solution:**
Create `docs/operations/KUBECONFIG-MANAGEMENT.md` covering:

1. **Storage Patterns**

   - Single kubeconfig with multiple contexts
   - Separate kubeconfig files per cluster
   - Environment-specific directories
   - Git-ignored secure storage

2. **Context Switching**

   - Using `KUBECONFIG` environment variable
   - Kubectx/Kubens tools
   - Devcontainer helper functions
   - VS Code Kubernetes extension

3. **Security Best Practices**

   - Never commit kubeconfigs to Git
   - Use short-lived tokens when possible
   - Rotate credentials regularly
   - Encrypt at rest

4. **Multi-Cluster Workflows**
   - Testing changes across clusters
   - Validating before production
   - Parallel operations
   - Cluster inventory management

**Workaround:**

- Use devcontainer functions: `hub`, `test`, `sno`, `current-cluster`
- Maintain separate terminal sessions per cluster
- Always verify context before running commands

**Related:**

- [TODO - Kubeconfig Management Guide](./TODO.md#operations)
- `.devcontainer/cluster-management.sh`

---

### Cleanup Script Coverage

**Status:** ⚠️ Incomplete

**Problem:**
Cleanup script doesn't handle all resources that can get stuck:

**Known Gaps:**

- ❌ Some CRDs not deleted in correct order
- ❌ Operators with finalizers may block
- ❌ PVCs not always cleaned up
- ❌ Some namespaces stuck in "Terminating"
- ❌ ApplicationSet-managed Applications not always cleaned

**Impact:**

- Manual intervention required for cleanup
- Cluster namespace pollution
- Testing iterations slowed down
- Resource quota exhaustion

**Proposed Solution:**

1. **Improve ordering:**

   - Delete CRs before CRDs
   - Delete apps before operators
   - Remove finalizers before deletion
   - Wait for graceful termination

2. **Add validation:**

   - Check for stuck resources
   - Report blocking resources
   - Suggest manual remediation steps

3. **Document patterns:**
   - Common stuck resource types
   - Remediation procedures
   - When to use force deletion

**Workaround:**

- Manually remove finalizers: `oc patch <resource> -p '{"metadata":{"finalizers":[]}}' --type=merge`
- Force delete namespaces: `oc delete namespace <name> --grace-period=0 --force`
- Delete CRDs manually if stuck

**Related:**

- [Cleanup Script Documentation](../scripts/README-cleanup-cluster.md)
- [TODO - Enhance Cleanup Script](./TODO.md#operations)

---

## 📊 Monitoring & Observability

### Centralized Logging

**Status:** ❌ Not Implemented

**Problem:**

- No centralized log aggregation
- Difficult to troubleshoot across multiple apps
- No log retention policy
- Manual checking of pod logs required

**Impact:**

- Time-consuming troubleshooting
- Logs lost when pods restart
- Difficult to correlate events across apps
- No long-term log analysis

**Proposed Solution:**

- Deploy OpenShift Logging (ELK stack)
- Or consider Loki + Grafana (lighter weight)
- Define log retention policies
- Create common queries and dashboards

**Workaround:**

- Use `oc logs` for individual pods
- Check application-specific logs via UI
- Export logs manually for analysis

**Related:**

- [TODO - Centralized Logging](./TODO.md#monitoring--observability)

---

### Metrics & Alerting

**Status:** ⚠️ Partial

**Problem:**

- VPA provides resource recommendations but no alerts
- Gatus monitors endpoints but limited alerting
- No custom application metrics
- No SLO/SLI tracking

**Impact:**

- Reactive rather than proactive operations
- May not detect issues until users report
- Difficult to track performance trends
- No capacity planning data

**Proposed Solution:**

- Deploy Prometheus + Grafana
- Define application-specific metrics
- Create alerting rules for critical conditions
- Implement SLO/SLI tracking

**Workaround:**

- Manual health checks via Gatus dashboard
- Periodic VPA report review
- OpenShift Console built-in metrics

**Related:**

- [Gatus Monitoring](../charts/platform/gatus/)
- [VPA Reporter](../scripts/README-vpa-goldilocks-reporter.md)

---

## 🔐 Security

### Secret Management

**Status:** ⚠️ Partially Addressed

**Problem:**

- External Secrets Operator deployed but not all apps migrated
- Some apps may still have hardcoded secrets
- No documented patterns for different secret types
- No secret rotation automation

**Impact:**

- Security risk from hardcoded credentials
- Difficult to rotate secrets across applications
- Inconsistent secret management patterns

**Proposed Solution:**

1. **Audit all charts:**

   - Identify hardcoded secrets
   - Create ExternalSecret resources
   - Document in chart README

2. **Create patterns:**

   - Basic auth secrets
   - TLS certificates (separate from cert-manager)
   - API keys/tokens
   - Database credentials

3. **Document workflows:**
   - Adding secrets to provider (Vault, AWS, etc.)
   - Creating ExternalSecret resources
   - Secret rotation procedures

**Workaround:**

- Use `values-secret.yaml` (git-ignored)
- Manual secret creation via `oc create secret`
- Document secrets needed in chart README

**Related:**

- [External Secrets Operator](../charts/platform/external-secrets-operator/)
- [Chart Standards - Secrets](./CHART-STANDARDS.md)

---

### Pod Security Standards

**Status:** ⚠️ Using Legacy SCC

**Problem:**

- Currently using OpenShift SecurityContextConstraints (SCC)
- Kubernetes is moving to Pod Security Admission (PSA)
- May need migration path for future OpenShift versions
- Some charts may not be "restricted" profile compliant

**Impact:**

- Potential deprecation of SCC in future
- Migration effort required
- Some apps may need security context updates

**Proposed Solution:**

1. **Audit chart compliance:**

   - Test against PSA "restricted" profile
   - Identify non-compliant charts
   - Document exceptions

2. **Create migration guide:**

   - SCC to PSA mapping
   - Chart update procedures
   - Testing methodology

3. **Update standards:**
   - Reference PSA in chart standards
   - Provide PSA-compliant examples

**Workaround:**

- Continue using SCC (currently supported)
- Ensure charts work with "restricted" SCC

**Related:**

- [Chart Standards - Security](./CHART-STANDARDS.md)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

---

## 🧪 Testing

### Automated Testing

**Status:** ❌ Not Implemented

**Problem:**

- No automated chart testing
- No integration tests
- Manual validation required
- Regressions may not be caught

**Impact:**

- Changes may break existing functionality
- Time-consuming manual testing
- Inconsistent test coverage
- Risky deployments

**Proposed Solution:**

1. **Unit Tests:**

   - Helm unittest plugin
   - Validate template rendering
   - Test value combinations

2. **Integration Tests:**

   - Deploy to test cluster
   - Validate application health
   - Test upgrade scenarios
   - Use Ginkgo/Gomega or similar

3. **CI/CD Integration:**
   - GitHub Actions workflows
   - Run on PR creation
   - Block merge on failure

**Workaround:**

- Manual testing in test cluster
- Use `helm template` to validate rendering
- Review changes carefully in PRs

**Related:**

- [TODO - Automated Testing](./TODO.md#testing--validation)

---

## 📚 Documentation

### Domain-Specific Documentation

**Status:** ⚠️ Incomplete

**Problem:**

- AI domain has good documentation
- Other domains lack detailed guides
- No architecture diagrams for domains
- Limited troubleshooting guides

**Impact:**

- Users may struggle with domain-specific apps
- Inconsistent documentation quality
- Difficult to onboard to specific domains

**Proposed Solution:**

- Create domain README files:
  - `docs/domains/media/README.md`
  - `docs/domains/home-automation/README.md`
  - `docs/domains/productivity/README.md`
  - `docs/domains/infrastructure/README.md`
- Include:
  - Domain overview
  - Application list with descriptions
  - Architecture diagrams
  - Common configurations
  - Troubleshooting guides

**Workaround:**

- Refer to individual chart README files
- Check AI domain docs for patterns
- Search GitHub discussions/issues

**Related:**

- [AI Stack Documentation](./ai-stack/)
- [TODO - Domain Documentation](./TODO.md#documentation)

---

### Video/Visual Documentation

**Status:** ❌ Not Available

**Problem:**

- All documentation is text-based
- No video tutorials
- Limited architecture diagrams
- No screencast walkthroughs

**Impact:**

- Steeper learning curve for visual learners
- Complex concepts harder to grasp
- Fewer community contributions

**Proposed Solution:**

- Create video content:
  - Quick start screencast (5-10 min)
  - Application deployment walkthrough (15 min)
  - ACM configuration guide (20 min)
  - Troubleshooting common issues (10 min)
- More diagrams:
  - Architecture diagrams per domain
  - Network flow diagrams
  - Security architecture
- Host on YouTube or similar

**Workaround:**

- Follow text documentation carefully
- Use example configurations
- Ask questions in discussions

---

## 🎯 Prioritization

### High Priority Gaps

1. **Documentation Consolidation** - Critical for usability
2. **Kubeconfig Management** - Essential for operations
3. **Image Build Automation** - Blocks custom app updates
4. **Template vs Config Separation** - Prevents framework breakage

### Medium Priority Gaps

1. **Cleanup Script Coverage** - Improves testing workflow
2. **Secret Management Migration** - Security improvement
3. **Domain Documentation** - Enhances user experience
4. **Automated Testing** - Reduces regression risk

### Low Priority Gaps

1. **Centralized Logging** - Nice to have, workarounds exist
2. **Video Documentation** - Enhances onboarding but not critical
3. **Pod Security Standards** - Future-proofing, not immediate

---

## 📝 How to Use This Document

### Reporting a Gap

1. Create GitHub issue with label "gap" or "limitation"
2. Describe the problem and impact
3. Suggest potential solutions
4. Reference this document in issue

### Closing a Gap

1. Implement solution
2. Update this document with "✅ Resolved" status
3. Link to PR or commit
4. Move to archive section if appropriate
5. Update related TODO items

---

## 🔗 Related Documentation

- [TODO List](./TODO.md) - Planned work items
- [Change Management](./CHANGE-MANAGEMENT.md) - How to make changes safely
- [Chart Exceptions](./CHART-EXCEPTIONS.md) - Documented standard deviations
- [Documentation Index](./INDEX.md) - All documentation

---

**Last Updated:** 2025-11-07
**Maintained By:** Repository maintainers
**Feedback:** Open an issue to report new gaps or suggest solutions
