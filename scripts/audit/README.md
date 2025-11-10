# Helm Chart Standards Audit Tool

Automated validation tool for ensuring Helm charts follow the standards defined in [CHART-STANDARDS.md](../docs/CHART-STANDARDS.md).

## Purpose

This tool audits application Helm charts to ensure they:

- Follow standard directory structure
- Use OpenShift-compatible security contexts
- Avoid cluster-scoped resources in app charts
- Include proper documentation
- Use Routes (OpenShift) by default with Ingress as fallback
- Have proper RBAC configuration
- Include recommended health checks and monitoring

## Usage

### Audit All Charts

```bash
python3 scripts/audit/audit-chart-standards.py --all
```

### Audit Specific Domain

```bash
python3 scripts/audit/audit-chart-standards.py --domain ai
python3 scripts/audit/audit-chart-standards.py --domain media
```

### Audit Single Chart

```bash
python3 scripts/audit/audit-chart-standards.py --chart charts/applications/ai/litellm
```

### Output Formats

```bash
# Human-readable text (default)
python3 scripts/audit/audit-chart-standards.py --all

# JSON format (for CI/CD integration)
python3 scripts/audit/audit-chart-standards.py --all --json

# Markdown format (for documentation)
python3 scripts/audit/audit-chart-standards.py --all --markdown > docs/reports/chart-audit-report.md
```

## Checks Performed

### Required Files

- ✅ Chart.yaml
- ✅ values.yaml
- ✅ README.md
- ✅ templates/\_helpers.tpl
- ✅ templates/NOTES.txt
- ✅ templates/deployment.yaml or statefulset.yaml
- ✅ templates/service.yaml
- ✅ templates/serviceaccount.yaml

### Recommended Files

- 🟡 values.schema.json
- 🟡 templates/route.yaml (OpenShift)
- 🟡 templates/networkpolicy.yaml
- 🟡 tests/test-connection.yaml

### OpenShift Guardrails

- ❌ No SecurityContextConstraints (platform responsibility)
- ❌ No ClusterRole/ClusterRoleBinding (platform responsibility)
- ❌ No StorageClass (platform responsibility)
- ✅ Namespace-scoped resources only

### Security Requirements

- ✅ `runAsNonRoot: true`
- ✅ `allowPrivilegeEscalation: false`
- ✅ `capabilities.drop: [ALL]`
- ❌ No `privileged: true`
- ❌ No `hostPath` volumes
- ❌ No hard-coded UIDs/FSGroups

### Documentation

- ✅ README with Prerequisites, Installation, Configuration sections
- ✅ values.yaml has required sections (image, service)
- ✅ Renovate comments for automated updates

### OpenShift Integration

- ✅ Route template exists (preferred)
- ✅ Ingress as optional fallback
- 🟡 ConsoleLink for console integration

## Exit Codes

- `0` - All charts compliant
- `1` - One or more charts non-compliant

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Chart Standards Audit

on:
  pull_request:
    paths:
      - "charts/applications/**"

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run chart audit
        run: |
          python3 scripts/audit/audit-chart-standards.py --all --json > audit-report.json
          python3 scripts/audit/audit-chart-standards.py --all --markdown > audit-report.md

      - name: Upload audit report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: |
            audit-report.json
            audit-report.md

      - name: Check compliance
        run: python3 scripts/audit/audit-chart-standards.py --all
```

### ArgoCD Pre-Sync Hook

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: chart-audit
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
spec:
  containers:
    - name: audit
      image: python:3.11-alpine
      command:
        - sh
        - -c
        - |
          pip install pyyaml
          python3 /scripts/audit/audit-chart-standards.py --all
      volumeMounts:
        - name: scripts
          mountPath: /scripts
  volumes:
    - name: scripts
      configMap:
        name: chart-audit-script
  restartPolicy: Never
```

## Report Example

```
================================================================================
HELM CHART STANDARDS AUDIT REPORT
================================================================================

Total Charts: 38
Compliant Charts: 30 (78.9%)
Non-Compliant Charts: 8

================================================================================
Domain: ai
================================================================================

✅ COMPLIANT | litellm v1.0.0 | Score: 95.5%
  Path: /workspaces/argo-apps/charts/applications/ai/litellm
  Checks: 21 passed, 1 failed

  Issues (3):
    🟡 [WARNING] Recommended file missing: values.schema.json [AUTO-FIX AVAILABLE]
       File: values.schema.json
    🟡 [WARNING] No Renovate comment found - automated image updates disabled [AUTO-FIX AVAILABLE]
       File: values.yaml
    ℹ️ [INFO] Route template found (OpenShift best practice)
       File: templates/route.yaml

❌ NON-COMPLIANT | open-webui v1.0.0 | Score: 68.2%
  Path: /workspaces/argo-apps/charts/applications/ai/open-webui
  Checks: 15 passed, 7 failed

  Issues (9):
    🔴 [ERROR] Missing 'runAsNonRoot: true' in securityContext [AUTO-FIX AVAILABLE]
       File: templates/deployment.yaml
    🔴 [ERROR] Cluster-scoped resource ClusterRole found in app chart (should be in platform)
       File: templates/clusterrole.yaml
    🟡 [WARNING] No Route template found - consider adding for OpenShift compatibility [AUTO-FIX AVAILABLE]
       File: templates/route.yaml
```

## Future Enhancements

- [ ] Auto-fix capability for common issues
- [ ] Custom rule configuration via `.chart-audit.yaml`
- [ ] Integration with Helm lint
- [ ] Chart comparison (before/after)
- [ ] Compliance history tracking
- [ ] Badge generation for README files
- [ ] Slack/Teams notifications
- [ ] Policy-as-code integration (OPA/Gatekeeper)

## Troubleshooting

### Import Error: yaml module not found

```bash
pip install pyyaml
```

### Permission Denied

```bash
chmod +x scripts/audit/audit-chart-standards.py
```

### Charts Not Found

Ensure you're running from the repository root:

```bash
cd /workspaces/argo-apps
python3 scripts/audit/audit-chart-standards.py --all
```

## Related Documentation

- [Chart Standards](../docs/CHART-STANDARDS.md) - Detailed standards documentation
- [Decision Tree](../docs/DECISION-TREE.md) - Deployment decision tree
- [Values Hierarchy](../docs/VALUES-HIERARCHY.md) - Values file structure
