# Adding a New Domain/ApplicationSet

This guide covers creating a new application domain (category) and its corresponding ApplicationSet.

## When to Create a New Domain

Create a new domain when you have a logical grouping of applications that:

- Share common characteristics or purpose
- Require similar configuration patterns
- Would benefit from centralized management
- Don't fit existing domains (ai, media, home-automation, productivity, infrastructure)

**Examples:**

- `gaming/` - Game servers and related tools
- `development/` - Developer tools and IDEs
- `communication/` - Chat, email, and messaging apps
- `monitoring/` - Observability and monitoring tools

## Directory Structure

```
charts/applications/<new-domain>/
├── <app1>/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── <app2>/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
└── ...

roles/<cluster>/
├── templates/
│   └── <new-domain>.yaml  # New ApplicationSet
└── values.yaml  # May need domain-specific config

.github/instructions/domains/
└── <new-domain>.md  # Domain-specific guidelines
```

## Step-by-Step Process

### 1. Create Domain-Specific Documentation

Create `.github/instructions/domains/<new-domain>.md`:

```markdown
---
applyTo: "charts/applications/<new-domain>/**"
---

# <New Domain> Domain - Application Guidelines

## Domain Overview

**Purpose:** <Brief description of domain purpose>

**ApplicationSet:** `roles/<cluster>/templates/<new-domain>.yaml`

**Common Characteristics:**

- <Key trait 1>
- <Key trait 2>
- <Key trait 3>

## Domain-Specific Requirements

### <Requirement Category 1>

<Guidelines and examples>

### <Requirement Category 2>

<Guidelines and examples>

## Standard Configuration Patterns

<Common values.yaml patterns for this domain>

## Testing and Validation

<Domain-specific testing requirements>
```

**See:** `.github/instructions/domains/ai.md` for a complete example

### 2. Create ApplicationSet Template in ALL Clusters

**CRITICAL:** Create the ApplicationSet template in **ALL FOUR** clusters: sno, hub, test, and template.

Create `roles/<cluster>/templates/<new-domain>.yaml` for each cluster:

```yaml
{{- if .Values.applicationSets.<new-domain>.enabled }}
---
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {{ .Release.Name }}-<new-domain>
  namespace: openshift-gitops
  annotations:
    argocd.argoproj.io/sync-wave: "100"  # Standard app wave
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]
  generators:
    - list:
        elements:
          # Applications listed here (commented by default)
          #- name: example-app
          #  gatus:
          #    enabled: true

  template:
    metadata:
      name: '{{ `{{.name}}` }}'
      namespace: openshift-gitops
      labels:
        cluster: {{ .Release.Name }}
        domain: <new-domain>

    spec:
      project: default

      source:
        repoURL: {{ .Values.cluster.repoURL }}
        targetRevision: {{ .Values.cluster.targetRevision }}
        path: charts/applications/<new-domain>/{{ `{{.name}}` }}
        helm:
          releaseName: '{{ `{{.name}}` }}'
          valuesObject:
            # Pass cluster config to all apps
            config: {{ .Values.config | toYaml | nindent 14 }}

      destination:
        server: https://kubernetes.default.svc
        namespace: '{{ `{{.name}}` }}'

      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - ServerSideApply=true
        retry:
          limit: 5
          backoff:
            duration: 5s
            factor: 2
            maxDuration: 3m

      # Optional: Add managed namespace metadata for operators
      # Uncomment if using VPA/Goldilocks for this domain
      #syncPolicy:
      #  managedNamespaceMetadata:
      #    labels:
      #      goldilocks.fairwinds.com/enabled: "true"
{{- end }}
```

### 3. Enable the ApplicationSet in Cluster Values

Add to `roles/<cluster>/values.yaml`:

```yaml
applicationSets:
  <new-domain>:
    enabled: true # or false to disable
```

**Note:** Start with `enabled: false` or only enable in test cluster initially.

### 4. Set Appropriate Sync Wave

Choose sync wave based on dependencies:

- **Wave 0**: Security, secrets (External Secrets Operator, RBAC)
- **Wave 50**: Storage, networking (MetalLB, storage operators)
- **Wave 100**: Standard applications (most domains)
- **Wave 200**: Configuration tweaks, post-deployment tasks

Update the `argocd.argoproj.io/sync-wave` annotation in the ApplicationSet.

### 5. Create First Application Chart

Follow the standard chart creation process:

```bash
./scripts/chart-tools/scaffold-new-chart.sh
# Select the new domain when prompted
```

Or manually create `charts/applications/<new-domain>/<app>/`:

- `Chart.yaml` - Chart metadata
- `values.yaml` - Default configuration
- `README.md` - Documentation
- `templates/` - Kubernetes manifests

**See:** `docs/CHART-STANDARDS.md` for complete chart requirements

### 6. Add Application to ApplicationSet

Edit `roles/<cluster>/templates/<new-domain>.yaml` and uncomment/add to elements list:

```yaml
generators:
  - list:
      elements:
        - name: your-new-app
          gatus:
            enabled: true
```

**Remember:** Add to ALL clusters (sno, hub, test, template), even if commented.

### 7. Update Documentation

#### Update `copilot-instructions.md`

Add domain to the list in "Key Directories" section:

```markdown
- `charts/applications/<domain>/<app>/` – Individual application Helm charts. Organized by domain: `ai/`, `media/`, `home-automation/`, `productivity/`, `infrastructure/`, **`<new-domain>/`**
```

Add to "Choose target ApplicationSet" section:

```markdown
Determine which functional group the app belongs to (`ai`, `media`, `base`, `home-automation`, `productivity`, `security`, `storage`, `tweaks`, **`<new-domain>`**)
```

#### Update Main README

Add domain description to the "Applications" section in `README.md`.

### 8. Test and Validate

1. **Render templates locally:**

   ```bash
   helm template test ./roles/test -s templates/<new-domain>.yaml
   ```

2. **Verify ApplicationSet syntax:**

   ```bash
   helm template test ./roles/test -s templates/<new-domain>.yaml | oc apply --dry-run=client -f -
   ```

3. **Deploy to test cluster:**

   - Commit changes to feature branch
   - Push to repository
   - Monitor Argo CD: `oc get applicationset -n openshift-gitops`
   - Check applications: `oc get applications -n openshift-gitops | grep <new-domain>`

4. **Validate deployment:**
   ```bash
   oc get pods -n <app-name>
   oc get route -n <app-name>
   ```

### 9. Cross-Cluster Verification

Verify ApplicationSet exists in all clusters:

```bash
for cluster in sno hub test template; do
  echo "=== $cluster ==="
  ls -la roles/$cluster/templates/<new-domain>.yaml || echo "MISSING!"
  grep -n "applicationSets:" roles/$cluster/values.yaml | head -5
done
```

## Common Patterns by Domain Type

### Infrastructure/Platform Domain

- Sync wave: **0-50** (early deployment)
- Often includes operators or CRDs
- May require cluster-level permissions
- Use `charts/platform/` instead of `charts/applications/` if truly platform-level

### Application Domain

- Sync wave: **100** (standard apps)
- Namespace-scoped resources only
- Standard security context (restricted SCC)
- Use `charts/applications/<domain>/`

### Configuration/Tweaks Domain

- Sync wave: **200** (post-deployment)
- ConfigMaps, tuning, optimization
- No long-running workloads
- May use Jobs instead of Deployments

## Troubleshooting

### ApplicationSet Not Created

- Check if enabled in cluster values: `cat roles/<cluster>/values.yaml | grep -A2 "<new-domain>"`
- Verify template syntax: `helm template <cluster> ./roles/<cluster> -s templates/<new-domain>.yaml`
- Check Argo CD logs: `oc logs -n openshift-gitops -l app.kubernetes.io/name=argocd-applicationset-controller`

### Applications Not Generated

- Verify elements list has uncommented entries
- Check template rendering: `helm template <cluster> ./roles/<cluster> -s templates/<new-domain>.yaml`
- Ensure chart path exists: `ls charts/applications/<new-domain>/<app>/Chart.yaml`

### Sync Failures

- Check sync wave order - dependencies must deploy first
- Verify namespace labels if using managedNamespaceMetadata
- Review Argo CD application status: `oc describe application <app-name> -n openshift-gitops`

## Best Practices

1. **Start Small:** Create domain with 1-2 applications initially, expand after validation
2. **Document Early:** Write domain guidelines before adding many applications
3. **Test First:** Always test in test cluster before enabling in production (sno)
4. **Consistent Naming:** Use lowercase with hyphens: `new-domain`, not `NewDomain` or `new_domain`
5. **Reuse Patterns:** Copy existing ApplicationSet templates and modify rather than starting from scratch
6. **Version Control:** Use feature branch for domain creation, PR for review before merging
7. **Monitor Deployment:** Watch Argo CD during first sync to catch issues early

## Checklist

- [ ] Domain purpose and scope clearly defined
- [ ] Domain-specific guidelines created in `.github/instructions/domains/<new-domain>.md`
- [ ] ApplicationSet template created in `roles/sno/templates/<new-domain>.yaml`
- [ ] ApplicationSet template created in `roles/hub/templates/<new-domain>.yaml`
- [ ] ApplicationSet template created in `roles/test/templates/<new-domain>.yaml`
- [ ] ApplicationSet template created in `roles/template/templates/<new-domain>.yaml`
- [ ] ApplicationSet enabled/disabled in all cluster values.yaml files
- [ ] Appropriate sync wave set based on domain type
- [ ] First application chart created and tested
- [ ] Documentation updated (copilot-instructions.md, README.md)
- [ ] Templates render successfully: `helm template <cluster> ./roles/<cluster> -s templates/<new-domain>.yaml`
- [ ] ApplicationSet deploys to test cluster successfully
- [ ] Applications sync and deploy successfully in test cluster
- [ ] Cross-cluster verification completed

## Related Documentation

- [Adding an Application Checklist](./adding-an-application-checklist.md)
- [ApplicationSet Workflow Guide](./adding-application.md)
- [Chart Standards](../../docs/CHART-STANDARDS.md)
- [Domain-Specific Guidelines](./domains/)
- [Bootstrap Process](../../bootstrap/README.md)

## Examples

**Existing Domains for Reference:**

- `charts/applications/ai/` - AI/ML applications
- `charts/applications/media/` - Media management
- `charts/applications/home-automation/` - IoT and smart home
- `charts/applications/productivity/` - Productivity tools
- `charts/applications/infrastructure/` - Infrastructure services

**ApplicationSet Templates:**

- `roles/sno/templates/ai.yaml` - AI domain ApplicationSet
- `roles/sno/templates/media.yaml` - Media domain ApplicationSet
- `roles/sno/templates/base-apps.yaml` - Base infrastructure ApplicationSet
