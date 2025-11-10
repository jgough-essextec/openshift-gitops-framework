# Instructions Index

Step-by-step instructions and workflows for common tasks in the argo-apps repository.

**Last Updated:** 2025-11-07

---

## 📚 Quick Navigation

- [Application Management](#application-management)
- [Domain-Specific Instructions](#domain-specific-instructions)
- [Cluster Management](#cluster-management)
- [Workflow Checklists](#workflow-checklists)

---

## Application Management

### Adding Applications

| Document                                                      | Description                               | Use When                          |
| ------------------------------------------------------------- | ----------------------------------------- | --------------------------------- |
| [Adding an Application](./adding-application.md)              | Core workflow for adding new applications | Adding any new app to any domain  |
| [Application Checklist](./adding-an-application-checklist.md) | **Required** checklist for new apps       | Every new application (mandatory) |
| [Adding a Domain](./adding-a-new-domain.md)                   | Create new application domains            | Creating new functional category  |

**Typical Flow:**

1. Read [Adding an Application](./adding-application.md) for overview
2. Check [Preferred Sources](../reference/PREFERRED-SOURCES.md) for where to find charts/images ([Quick Ref](../reference/APPLICATION-SOURCES-QUICK-REF.md))
3. Review domain-specific instructions below
4. Follow [Application Checklist](./adding-an-application-checklist.md) step-by-step
5. Run audit tool to verify compliance

---

## Domain-Specific Instructions

Each application domain has specific requirements and patterns.

### AI Domain

**File:** [domains/ai.md](./domains/ai.md)

**Scope:**

- AI/ML applications
- LLM providers (Ollama, LiteLLM)
- AI interfaces (Open WebUI)
- Model management

**Key Considerations:**

- GPU resource requirements
- Model storage (PVCs)
- API key management
- Network policies for external APIs

---

### Media Domain

**File:** [domains/media.md](./domains/media.md)

**Scope:**

- Media servers (Plex, Jellyfin)
- Content acquisition (Sonarr, Radarr, Prowlarr)
- Request management (Overseerr)
- Download clients

**Key Considerations:**

- Large storage requirements
- Network policies for P2P
- Hardware transcoding (GPU)
- Content organization

---

### Home Automation Domain

**File:** [domains/home-automation.md](./domains/home-automation.md)

**Scope:**

- Smart home platforms (Home Assistant)
- Automation engines (Node-RED)
- MQTT brokers (EMQX)
- Device integrations (ZwaveJS2MQTT)

**Key Considerations:**

- Device discovery requirements
- Network access patterns
- Real-time communication
- USB device passthrough

---

### Productivity Domain

**File:** [domains/productivity.md](./domains/productivity.md)

**Scope:**

- Bookmark managers
- Diagram tools (Excalidraw)
- Development utilities (IT-Tools, CyberChef)
- Portal applications (Startpunkt)

**Key Considerations:**

- User authentication
- Data persistence
- Browser compatibility
- Simple resource requirements

---

### Infrastructure Domain

**File:** [domains/infrastructure.md](./domains/infrastructure.md)

**Scope:**

- Document management (Paperless)
- Data processing (Glue Worker)
- Monitoring integrations
- Custom business logic

**Key Considerations:**

- Database requirements
- API integrations
- Custom image builds
- Background job processing

---

## Cluster Management

### Multi-Cluster Operations

| Document                                                              | Description                                        |
| --------------------------------------------------------------------- | -------------------------------------------------- |
| [Kubeconfig Management](../operations/KUBECONFIG-MANAGEMENT.md)       | Managing cluster credentials and context switching |
| [Multi-Cluster Management](../operations/MULTI-CLUSTER-MANAGEMENT.md) | Working with multiple clusters simultaneously      |

### Deployment Patterns

| Document                                                                 | Description                             |
| ------------------------------------------------------------------------ | --------------------------------------- |
| [Deployment Options](../deployment/DEPLOYMENT-OPTIONS.md)                | Choose the right deployment pattern     |
| [Single Cluster Quick Start](../deployment/single-cluster-quickstart.md) | Deploy to one cluster                   |
| [Multi-Cluster Quick Start](../deployment/multi-cluster-quickstart.md)   | Deploy to multiple clusters without ACM |
| [ACM Quick Start](../deployment/acm-quickstart.md)                       | Deploy with Advanced Cluster Management |
| [Multi-Site Quick Start](../deployment/multi-site-quickstart.md)         | Deploy across multiple sites            |

---

## Workflow Checklists

### Change Management

| Checklist                                                                  | Use When                           |
| -------------------------------------------------------------------------- | ---------------------------------- |
| [Moving Charts](../CHANGE-MANAGEMENT.md#moving-charts)                     | Relocating chart directories       |
| [Editing ApplicationSets](../CHANGE-MANAGEMENT.md#editing-applicationsets) | Modifying ApplicationSet templates |
| [Adding Applications](../CHANGE-MANAGEMENT.md#adding-applications)         | New app workflow                   |
| [Removing Applications](../CHANGE-MANAGEMENT.md#removing-applications)     | Deprecating/removing apps          |
| [Updating Operators](../CHANGE-MANAGEMENT.md#updating-operators)           | Operator version updates           |

### Pre-Flight Checks

Before making any changes:

- [ ] Review relevant [Architectural Decision Records](../decisions/)
- [ ] Check [Chart Standards](../CHART-STANDARDS.md)
- [ ] Verify [Chart Exceptions](../CHART-EXCEPTIONS.md) if deviation needed
- [ ] Consult [Change Management Guide](../CHANGE-MANAGEMENT.md)
- [ ] Run `current-cluster` to verify correct cluster context

### Post-Change Validation

After making changes:

- [ ] Run chart audit: `scripts/audit/audit-chart-standards.py --chart <path>`
- [ ] Test rendering: `helm template <release> <path> -f values-<cluster>.yaml`
- [ ] Check for errors: `oc get applications -n openshift-gitops`
- [ ] Verify deployment: `oc get pods -n <namespace>`
- [ ] Update relevant documentation
- [ ] Add to cleanup script if new resources added

---

## Quick Reference by Task

### I Want to Add an Application

1. **Check for operator first:** [Preferred Sources](../reference/PREFERRED-SOURCES.md)
2. **Read domain instructions:** [Domain-Specific](#domain-specific-instructions)
3. **Follow core workflow:** [Adding an Application](./adding-application.md)
4. **Use checklist:** [Application Checklist](./adding-an-application-checklist.md)
5. **Validate:** Run audit tool

### I Want to Create a New Domain

1. **Read domain guide:** [Adding a Domain](./adding-a-new-domain.md)
2. **Review architecture:** [Detailed Overview](../DETAILED-OVERVIEW.md)
3. **Check change management:** [Change Management Guide](../CHANGE-MANAGEMENT.md)
4. **Create ApplicationSet chart**
5. **Update all role templates**

### I Want to Deploy to a New Cluster

1. **Choose deployment pattern:** [Deployment Options](../deployment/DEPLOYMENT-OPTIONS.md)
2. **Follow quick start:** Select appropriate guide
3. **Configure values:** [Values Hierarchy](../VALUES-HIERARCHY.md)
4. **Bootstrap cluster:** Follow bootstrap README
5. **Verify deployment**

### I Want to Troubleshoot an Issue

1. **Check current cluster:** Run `current-cluster`
2. **Review troubleshooting guides:** [Troubleshooting](../troubleshooting/)
3. **Check application health:** Gatus dashboard or `oc get pods`
4. **Review logs:** `oc logs -n <namespace> <pod>`
5. **Consult known gaps:** [Known Gaps](../KNOWN-GAPS.md)

### I Want to Update Documentation

1. **Check documentation standards:** [INDEX.md footer](../INDEX.md)
2. **Update relevant doc file**
3. **Update INDEX.md if new file:** Add to appropriate section
4. **Update copilot instructions:** If workflow changes
5. **Check for broken links**

---

## Standards & Guidelines

### Before Creating New Instructions

1. **Check if it already exists:** Search docs/ and this index
2. **Determine appropriate location:**
   - Application task → `docs/instructions/`
   - Operational task → `docs/operations/`
   - Deployment task → `docs/deployment/`
   - Reference material → `docs/reference/`
3. **Follow naming convention:** `UPPERCASE-WITH-DASHES.md` for guides
4. **Include metadata:** Purpose, last updated, related docs
5. **Add to this index:** Maintain discoverability

### Instruction Document Structure

```markdown
# Task Name

Brief description of what this instruction covers.

**Last Updated:** YYYY-MM-DD

---

## Prerequisites

- List prerequisites
- Required tools
- Permissions needed

## Steps

### Step 1: Clear Title

Description and commands

### Step 2: Clear Title

Description and commands

## Validation

How to verify completion

## Troubleshooting

Common issues and solutions

## Related Documentation

- Link to related docs
```

---

## External Resources

### Kubernetes & OpenShift

- [OpenShift Documentation](https://docs.openshift.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Argo CD Documentation](https://argo-cd.readthedocs.io/)

### Validated Patterns

- [Validated Patterns Framework](https://validatedpatterns.io/)
- [Red Hat Patterns GitHub](https://github.com/validatedpatterns)

### Tools

- [ArtifactHub](https://artifacthub.io/)
- [OperatorHub.io](https://operatorhub.io/)
- [Quay.io](https://quay.io/)
- [Docker Hub](https://hub.docker.com/)

---

## 📚 Related Documentation

- [Documentation Index](../INDEX.md) - All documentation
- [Chart Standards](../CHART-STANDARDS.md) - Required standards
- [Change Management](../CHANGE-MANAGEMENT.md) - Change checklists
- [Preferred Sources](../reference/PREFERRED-SOURCES.md) - Where to find apps

---

**Maintained By:** Repository maintainers
**Feedback:** Open an issue or PR to suggest improvements
**See Also:** [Documentation Index](../INDEX.md) for all available documentation
