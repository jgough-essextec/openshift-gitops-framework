# Scripts & Tools

This directory contains utility scripts and tools for managing the OpenShift GitOps environment.

## 📁 Directory Structure

```
scripts/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── adr-validation/               # ADR validation tools
├── audit/                        # Chart compliance auditing
├── chart-tools/                  # Chart development tools
├── cluster-operations/           # Cluster management tools
├── reporting/                    # Reporting and analytics
├── maintenance/                  # Maintenance automation
└── icon-tools/                   # Icon validation tools
```

## 📋 ADR Validation Tools

Located in `adr-validation/`:

Tools for validating and maintaining Architectural Decision Records (ADRs) following the MADR format.

### Check ADR Numbering

**File:** `adr-validation/check_adr_numbering.py`

Validates ADR file numbering sequence.

**Usage:**

```bash
python3 scripts/adr-validation/check_adr_numbering.py
```

**Checks:**

- Sequential numbering (0000, 0001, 0002, ...)
- No gaps in sequence
- No duplicate numbers
- Proper filename format: `NNNN-title.md`

### Check ADR Metadata

**File:** `adr-validation/check_adr_metadata.py`

Validates YAML frontmatter metadata in ADRs.

**Usage:**

```bash
# Validate all ADRs
python3 scripts/adr-validation/check_adr_metadata.py

# Validate specific ADR
python3 scripts/adr-validation/check_adr_metadata.py docs/decisions/0001-use-openshift.md
```

**Checks:**

- Required `status` field (proposed, accepted, rejected, deprecated, superseded)
- Recommended `date` field (YYYY-MM-DD format)
- Recommended `decision-makers` field

### Validate ADR Structure

**File:** `adr-validation/validate_adr.py`

Validates ADR structure according to MADR format.

**Usage:**

```bash
# Validate all ADRs
python3 scripts/adr-validation/validate_adr.py

# Validate specific ADR
python3 scripts/adr-validation/validate_adr.py docs/decisions/0001-use-openshift.md
```

**Checks:**

- Title presence (H1 heading)
- Required sections: Context, Decision, Consequences
- Recommended sections: Decision Drivers, Considered Options, Pros and Cons
- YAML frontmatter presence
- Content length (warns if < 100 words)

### Generate ADR Index

**File:** `adr-validation/generate_adr_index.py`

Automatically generates an ADR index from ADR files.

**Usage:**

```bash
python3 scripts/adr-validation/generate_adr_index.py
```

**Output:**

- Grouped by status (Accepted, Proposed, Deprecated, etc.)
- Chronological list
- Automatically updated timestamps

**Note:** Our ADR index at `docs/decisions/INDEX.md` is manually maintained with enhanced formatting. Use this script to verify all ADRs are included.

**Documentation:** See `adr-validation/README.md` for detailed usage.

## 🔍 Audit Tools

Located in `audit/`:

### Chart Standards Audit

**File:** `audit/audit-chart-standards.py`

Validates Helm charts against standards defined in `docs/CHART-STANDARDS.md`.

**Usage:**

```bash
# Audit single chart
python3 scripts/audit/audit-chart-standards.py --chart charts/applications/ai/litellm

# Audit entire domain
python3 scripts/audit/audit-chart-standards.py --domain ai

# Audit all charts
python3 scripts/audit/audit-chart-standards.py --all

# Generate markdown report
python3 scripts/audit/audit-chart-standards.py --all --markdown > report.md

# JSON output for CI/CD
python3 scripts/audit/audit-chart-standards.py --all --json
```

**What it checks:**

- Required files (Chart.yaml, values.yaml, README.md, templates/, etc.)
- Security context compliance (OpenShift restricted SCC)
- OpenShift guardrails (no SCCs, ClusterRoles in app charts)
- values.yaml structure
- Documentation completeness
- CRD location validation
- Renovate integration

**Documentation:** See `audit/README.md` for detailed usage.

## 🛠️ Chart Development Tools

Located in `chart-tools/`:

### Scaffold New Chart

**File:** `chart-tools/scaffold-new-chart.sh`

Creates a new Helm chart with standards-compliant structure.

**Usage:**

```bash
./scripts/chart-tools/scaffold-new-chart.sh
# Follow interactive prompts to select domain and app name
```

**Creates:**

- Chart.yaml with proper metadata
- values.yaml with standard structure
- README.md template
- templates/\_helpers.tpl
- templates/NOTES.txt
- All required templates (deployment, service, route, etc.)

### Verify App in All Clusters

**File:** `chart-tools/verify-app-in-all-clusters.sh`

Verifies an application is added to all cluster roles (sno, hub, test, template).

**Usage:**

```bash
./scripts/chart-tools/verify-app-in-all-clusters.sh <app-name>
```

**Example:**

```bash
./scripts/chart-tools/verify-app-in-all-clusters.sh litellm
```

### Validate Icons

**File:** `chart-tools/validate-icons.sh`

Validates that chart icons are valid Material Design Icons.

**Usage:**

```bash
./scripts/chart-tools/validate-icons.sh
```

## 🖥️ Cluster Operations

Located in `cluster-operations/`:

### Cleanup Cluster

**File:** `cluster-operations/cleanup-cluster.sh`

Removes applications and cleans up cluster resources.

**Usage:**

```bash
./scripts/cluster-operations/cleanup-cluster.sh [options]
```

**Features:**

- Remove specific applications
- Clean up orphaned resources
- Reset cluster to baseline state
- Dry-run mode for safety

**⚠️ WARNING:** This script can remove applications. Always review before executing.

### Diagnose TrueNAS CSI

**File:** `cluster-operations/diagnose-truenas-csi.sh`

Diagnoses TrueNAS CSI driver issues and provides troubleshooting information.

**Usage:**

```bash
./scripts/cluster-operations/diagnose-truenas-csi.sh
```

**Checks:**

- CSI driver pods status
- Storage classes configuration
- PVC binding issues
- TrueNAS API connectivity
- Volume provisioning logs

## 📊 Reporting Tools

Located in `reporting/`:

### VPA Goldilocks Reporter

**Files:**

- `reporting/vpa-goldilocks-reporter.py`
- `reporting/vpa-reporter-config.yaml`

Generates reports from Vertical Pod Autoscaler (VPA) recommendations via Goldilocks.

**Usage:**

```bash
# Generate report with default config
python3 scripts/reporting/vpa-goldilocks-reporter.py

# Use custom config
python3 scripts/reporting/vpa-goldilocks-reporter.py --config scripts/reporting/vpa-reporter-config.yaml
```

**Output:**

- Resource usage analysis
- VPA recommendations per application
- Cost optimization suggestions
- CSV/JSON export options

**Configuration:** Edit `vpa-reporter-config.yaml` to customize:

- Goldilocks endpoint
- Report format
- Filter criteria
- Output location

## 🔧 Maintenance Tools

Located in `maintenance/`:

### Update Error Pages

**File:** `maintenance/update-error-pages.py`

Updates custom error pages for OpenShift Routes.

**Usage:**

```bash
python3 scripts/maintenance/update-error-pages.py [options]
```

**Features:**

- Update error pages across all routes
- Customize error page content
- Backup before changes
- Selective updates by namespace

### Update Kasten Excluded Apps

**File:** `maintenance/update-kasten-excluded-apps.sh`

Updates Kasten K10 backup exclusion labels for applications.

**Usage:**

```bash
./scripts/maintenance/update-kasten-excluded-apps.sh
```

**Purpose:**

- Mark apps that shouldn't be backed up
- Update backup policies
- Exclude ephemeral workloads
- Manage backup scope

## 🎨 Icon Tools

Located in `icon-tools/`:

### Check CBI Icons

**File:** `icon-tools/check-cbi-icons.py`

Validates ConsoleLink icons against available Material Design Icons.

**Usage:**

```bash
python3 scripts/icon-tools/check-cbi-icons.py
```

### Find Icons

**File:** `icon-tools/find-icons.py`

Searches available Material Design Icons by keyword.

**Usage:**

```bash
python3 scripts/icon-tools/find-icons.py <search-term>
```

**Example:**

```bash
python3 scripts/icon-tools/find-icons.py database
python3 scripts/icon-tools/find-icons.py ai
```

## 📦 Dependencies

Python scripts require dependencies from `requirements.txt`:

```bash
pip install -r scripts/requirements.txt
```

**Required packages:**

- PyYAML - YAML parsing
- requests - HTTP requests
- jinja2 - Template rendering
- (See requirements.txt for complete list)

## 🚀 Quick Start

### For New Applications

1. **Create chart:**

   ```bash
   ./scripts/chart-tools/scaffold-new-chart.sh
   ```

2. **Validate chart:**

   ```bash
   python3 scripts/audit/audit-chart-standards.py --chart charts/applications/<domain>/<app>
   ```

3. **Verify cross-cluster:**
   ```bash
   ./scripts/chart-tools/verify-app-in-all-clusters.sh <app-name>
   ```

### For Existing Applications

1. **Audit compliance:**

   ```bash
   python3 scripts/audit/audit-chart-standards.py --all
   ```

2. **Check VPA recommendations:**

   ```bash
   python3 scripts/reporting/vpa-goldilocks-reporter.py
   ```

3. **Validate icons:**
   ```bash
   ./scripts/chart-tools/validate-icons.sh
   ```

## 🔗 Related Documentation

- **[Chart Standards](../docs/CHART-STANDARDS.md)** - Requirements for charts
- **[Adding Applications](../.github/instructions/adding-application-checklist.md)** - Step-by-step guide
- **[Troubleshooting](../docs/troubleshooting/)** - Problem resolution guides
- **[Audit Tool Documentation](audit/README.md)** - Detailed audit tool usage

## 🤝 Contributing

When adding new scripts:

1. Place in appropriate subdirectory (audit/, chart-tools/, etc.)
2. Include usage comments at top of script
3. Update this README with script description
4. Add to CI/CD workflows if applicable
5. Document dependencies in requirements.txt

## 📝 Script Naming Conventions

- Use lowercase with hyphens: `my-script.sh`
- Python scripts: `.py` extension
- Shell scripts: `.sh` extension
- Config files: `.yaml` or `.json`
- Documentation: `README.md` in each subdirectory

## 🧪 Testing Scripts

Before committing:

1. Test in dry-run mode (if available)
2. Test on non-production cluster
3. Verify error handling
4. Check for proper exit codes
5. Validate output format

## 🛡️ Safety Guidelines

**Before running cluster operations:**

- ✅ Verify cluster context: `current-cluster`
- ✅ Review script actions
- ✅ Use dry-run mode when available
- ✅ Have backups for production changes
- ⚠️ Never run destructive scripts on production without testing

**For automation/CI/CD:**

- Use `--json` flag for parseable output
- Check exit codes for success/failure
- Log all script executions
- Use service accounts with minimal permissions
- Implement proper error handling

## 💡 Tips & Best Practices

1. **Audit regularly:** Run chart audit weekly to track compliance
2. **Automate validation:** Add audit checks to pre-commit hooks
3. **Monitor resources:** Review VPA reports monthly for optimization
4. **Keep icons current:** Validate icons when updating charts
5. **Document changes:** Update scripts/README.md when adding tools

## 📞 Support

For script issues or questions:

- Check script documentation: `<script> --help`
- Review tool-specific README in subdirectories
- Consult troubleshooting guides in `docs/troubleshooting/`
- Check ADRs for architectural context: `docs/decisions/`
