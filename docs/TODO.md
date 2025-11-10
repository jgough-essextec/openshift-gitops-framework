# TODO List

Planned improvements, features, and tasks for the argo-apps repository.

**Last Updated:** 2025-11-07

---

## 🎯 High Priority

### Documentation Improvements

- [ ] **Create quick start guides for each deployment pattern**

  - Status: In progress
  - Files needed:
    - `docs/deployment/single-cluster-quickstart.md`
    - `docs/deployment/multi-cluster-quickstart.md`
    - `docs/deployment/acm-quickstart.md`
    - `docs/deployment/multi-site-quickstart.md`
  - Related: [Deployment Options](./deployment/DEPLOYMENT-OPTIONS.md)

- [ ] **Consolidate GitHub/Copilot instructions into docs/**

  - Status: Planned
  - Move `.github/instructions/*` to `docs/instructions/`
  - Create `docs/instructions/INDEX.md`
  - Update `.github/copilot-instructions.md` with new references
  - Related: [Known Gaps - Documentation Organization](#documentation-organization)

- [ ] **Create configuration guide separating templates from user configs**
  - Status: Planned
  - File: `docs/CONFIGURATION-GUIDE.md`
  - Document template files vs cluster-specific files
  - Provide guidance on what to customize
  - Related: [Known Gaps - Template vs Configuration](#template-vs-configuration-separation)

### Application Management

- [ ] **Document apps requiring custom image builds**

  - Status: Identified (see [Known Gaps](#applications-requiring-custom-images))
  - Create build pipelines/instructions
  - Document dependencies and build requirements
  - Consider GitHub Actions or Tekton pipelines

- [ ] **Standardize operator deployment patterns**
  - Status: Planned
  - Document operator-first approach
  - Create templates for OLM-based operators
  - Add operator examples to chart standards

### Operations

- [ ] **Improve kubeconfig management documentation**

  - Status: Planned
  - File: `docs/operations/KUBECONFIG-MANAGEMENT.md`
  - Document storage patterns
  - Rotation procedures
  - Multi-cluster switching best practices
  - Devcontainer integration

- [ ] **Enhance cleanup script coverage**
  - Status: Ongoing
  - Add newly discovered stuck resources
  - Improve ordering (CRs before CRDs)
  - Add validation checks
  - Related: [Known Gaps - Cleanup Script Coverage](#cleanup-script-coverage)

---

## 📋 Medium Priority

### Chart Improvements

- [ ] **Audit all charts for standards compliance**

  - Status: Tooling exists, needs execution
  - Run `scripts/audit/audit-chart-standards.py --all`
  - Fix identified issues
  - Document exceptions in `docs/CHART-EXCEPTIONS.md`

- [ ] **Add topology awareness to all charts**

  - Status: Partial (AI and Media complete)
  - Infrastructure charts need updates
  - Home automation charts need updates
  - Productivity charts need updates
  - Use `update-*-charts-topology.py` scripts as templates

- [ ] **Implement consistent resource requests/limits**
  - Status: Inconsistent across charts
  - Define size profiles (small, medium, large)
  - Apply VPA recommendations
  - Document in chart standards

### Testing & Validation

- [ ] **Create automated chart validation in CI/CD**

  - Status: Planned
  - Integrate audit tool into GitHub Actions
  - Add Helm lint checks
  - Validate values files
  - Test rendering for each topology

- [ ] **Develop integration tests for common scenarios**
  - Status: Not started
  - Test application deployment
  - Test multi-cluster scenarios
  - Test ACM configurations
  - Consider using Ginkgo/Gomega or similar

### Security

- [ ] **Complete external secrets migration**

  - Status: Ongoing
  - Identify all apps with hardcoded secrets
  - Migrate to external-secrets-operator
  - Document secret management patterns

- [ ] **Implement Pod Security Admission**
  - Status: Planned
  - Move from SecurityContextConstraints to PSA
  - Validate restricted profile compliance
  - Update chart standards

---

## 🔧 Low Priority

### Automation

- [ ] **Create application scaffolding wizard**

  - Status: Idea
  - Interactive CLI tool
  - Prompt for app details
  - Generate complete chart structure
  - Run checklist validation

- [ ] **Automate role template synchronization**
  - Status: Script exists (`sync-role-templates.sh`)
  - Add to GitHub Actions
  - Trigger on template changes
  - Validate consistency

### Monitoring & Observability

- [ ] **Expand Gatus monitoring coverage**

  - Status: Partial
  - Add health checks for all apps
  - Document endpoint patterns
  - Create dashboard templates

- [ ] **Implement centralized logging**
  - Status: Not started
  - Consider OpenShift Logging or ELK
  - Define log retention policies
  - Document log aggregation patterns

### Developer Experience

- [ ] **Improve devcontainer tooling**

  - Status: Basic functionality exists
  - Add more cluster management helpers
  - Improve multi-cluster switching UX
  - Add validation tools

- [ ] **Create VS Code workspace settings**
  - Status: Not started
  - Configure YAML schemas
  - Add recommended extensions
  - Set up task runners

---

## 🌟 Future Enhancements

### Advanced Features

- [ ] **Multi-tenancy support**

  - Namespace isolation
  - RBAC templates
  - Resource quotas
  - Network policies

- [ ] **Cost optimization tooling**

  - Resource usage reports
  - Right-sizing recommendations
  - Idle resource detection
  - Cost allocation by domain

- [ ] **Backup/Restore automation**
  - Expand Kasten K10 integration
  - Document backup strategies
  - Create restore procedures
  - Test DR scenarios

### Platform Capabilities

- [ ] **Add more platform components**

  - Service mesh (Istio/Maistra)
  - Observability stack (Prometheus, Grafana, Jaeger)
  - CI/CD tooling (Tekton, Jenkins)
  - Developer portal (Backstage)

- [ ] **Expand GPU support**
  - NVIDIA GPU operator enhancements
  - AMD GPU workload examples
  - Intel GPU support
  - GPU scheduling patterns

### Documentation

- [ ] **Create video tutorials**

  - Quick start screencast
  - Application deployment walkthrough
  - Troubleshooting common issues
  - ACM configuration guide

- [ ] **Write troubleshooting playbooks**
  - Structured problem-solution format
  - Decision trees for diagnosis
  - Common error patterns
  - Resolution procedures

---

## 📝 Recurring Tasks

### Weekly

- [ ] Review and triage new issues
- [ ] Update application versions (Renovate PRs)
- [ ] Check for security vulnerabilities
- [ ] Monitor cluster health

### Monthly

- [ ] Audit chart compliance (`scripts/audit/audit-chart-standards.py --all`)
- [ ] Review VPA recommendations (`scripts/reporting/vpa-goldilocks-reporter.py`)
- [ ] Update documentation for changes
- [ ] Validate backup/restore procedures

### Quarterly

- [ ] Review and update ADRs
- [ ] Assess new platform capabilities
- [ ] Evaluate new applications to add
- [ ] Review and optimize resource usage
- [ ] Update devcontainer tooling

---

## 🔗 Related Documentation

- [Known Gaps](./KNOWN-GAPS.md) - Identified limitations
- [Change Management](./CHANGE-MANAGEMENT.md) - Change checklists
- [Documentation Index](./INDEX.md) - All documentation

---

## 📌 How to Use This Document

### Adding a TODO

1. Choose appropriate priority section
2. Create descriptive title with checkbox
3. Add status indicator
4. List specific tasks or files
5. Reference related documentation

### Completing a TODO

1. Check the checkbox: `- [x]`
2. Update status to "Complete"
3. Add completion date
4. Link to PR or commit
5. Update related documentation

### Priority Definitions

- **High Priority:** Critical for core functionality or blocking other work
- **Medium Priority:** Important but not blocking, improves quality
- **Low Priority:** Nice to have, enhances user experience
- **Future:** Long-term vision, requires significant effort

---

**Maintainer Notes:**

- Review this list monthly
- Move completed items to archive
- Adjust priorities based on user feedback
- Keep descriptions actionable
