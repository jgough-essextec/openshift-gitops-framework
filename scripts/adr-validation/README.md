# Validation and Automation Scripts

This directory contains scripts for validating and maintaining the OpenShift-Arch repository.

## ADR Validation Scripts

### `validate_adr.py`

Validates ADR structure according to MADR (Markdown Architectural Decision Records) format.

**Usage:**
```bash
# Validate all ADRs
python3 scripts/validate_adr.py

# Validate specific ADR
python3 scripts/validate_adr.py adr-files/001-cluster-deployment-models.md
```

**Checks:**
- Title presence (H1 heading)
- Required sections: Context, Decision, Consequences
- Recommended sections: Decision Drivers, Considered Options, Pros and Cons
- YAML frontmatter presence
- Content length (warns if < 100 words)

### `check_adr_numbering.py`

Validates ADR numbering sequence to ensure no gaps or duplicates.

**Usage:**
```bash
python3 scripts/check_adr_numbering.py
```

**Checks:**
- Sequential numbering (001, 002, 003, ...)
- No gaps in sequence
- No duplicate numbers
- Proper filename format: `NNN-title.md`

### `check_adr_metadata.py`

Validates YAML frontmatter metadata in ADRs.

**Usage:**
```bash
# Validate all ADRs
python3 scripts/check_adr_metadata.py

# Validate specific ADR
python3 scripts/check_adr_metadata.py adr-files/001-cluster-deployment-models.md
```

**Checks:**
- **Required:** `status` field (proposed, accepted, rejected, deprecated, superseded)
- **Recommended:** `date` field (YYYY-MM-DD format)
- **Recommended:** `decision-makers` field
- Common typos (e.g., "superceded" vs "superseded")

### `generate_adr_index.py`

Automatically generates the `adr-index.md` file from ADR files.

**Usage:**
```bash
python3 scripts/generate_adr_index.py
```

**Output:**
- Grouped by status (Accepted, Proposed, Deprecated, etc.)
- Chronological list
- Legend and usage instructions
- Automatically updated timestamps

### `validate_cross_refs.py`

Validates internal markdown links across the repository.

**Usage:**
```bash
python3 scripts/validate_cross_refs.py
```

**Checks:**
- Broken internal links
- Missing referenced files
- Invalid relative paths

---

## Usage in Workflows

### GitHub Actions

These scripts run automatically in GitHub Actions workflows:

- **On PR:** Validates ADR structure, numbering, and metadata
- **On Push:** Checks ADR index is up-to-date
- **Manual Trigger:** Can be run via `workflow_dispatch`

See `.github/workflows/adr-validation.yaml` for configuration.

### Pre-commit Hooks

These scripts run as pre-commit hooks when configured:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

See `.pre-commit-config.yaml` for configuration.

---

## Development

### Requirements

- Python 3.11+
- Standard library only (no external dependencies)

### Adding New Validation

To add a new validation script:

1. Create script in `scripts/` directory
2. Follow naming convention: `validate_*.py` or `check_*.py`
3. Include docstring and usage instructions
4. Add to `.github/workflows/adr-validation.yaml`
5. Add to `.pre-commit-config.yaml`
6. Update this README

### Testing

Test scripts locally before committing:

```bash
# Test individual script
python3 scripts/validate_adr.py

# Test all validation scripts
python3 scripts/check_adr_numbering.py
python3 scripts/check_adr_metadata.py
python3 scripts/validate_adr.py
python3 scripts/validate_cross_refs.py

# Generate index
python3 scripts/generate_adr_index.py
```

---

## Troubleshooting

### Common Issues

**Issue:** Script fails with "ModuleNotFoundError"  
**Solution:** Scripts use only Python standard library. Ensure Python 3.11+ is installed.

**Issue:** "Permission denied" error  
**Solution:** Make scripts executable: `chmod +x scripts/*.py`

**Issue:** Pre-commit hooks not running  
**Solution:** Ensure hooks are installed: `pre-commit install`

**Issue:** GitHub Actions workflow fails  
**Solution:** Check workflow logs for specific error messages

---

## References

- [ADR Validation Documentation](../docs/development/ADR-VALIDATION.md) (if exists)
- [Automation Practices Guide](../shared/automation/README.md)
- [Contributing Guidelines](../CONTRIBUTING.md) (if exists)

---

**Version:** 1.0  
**Last Updated:** 2025-11-07  
**Maintained By:** Platform Engineering Team
