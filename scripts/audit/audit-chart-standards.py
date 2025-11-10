#!/usr/bin/env python3
"""
Helm Chart Standards Audit Tool

Validates application Helm charts against the standards defined in CHART-STANDARDS.md
Generates a compliance report showing which charts follow best practices.

Usage:
    python3 scripts/audit-chart-standards.py [--chart path/to/chart] [--domain domain-name] [--fix]

Options:
    --chart PATH    Audit a single chart
    --domain NAME   Audit all charts in a domain (ai, media, etc.)
    --all          Audit all application charts (default)
    --fix          Attempt to auto-fix common issues
    --json         Output in JSON format
    --markdown     Output markdown report
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

@dataclass
class ChartIssue:
    """Represents a standards compliance issue"""
    severity: str  # "error", "warning", "info"
    category: str  # "structure", "security", "openshift", "documentation"
    message: str
    file: Optional[str] = None
    fixable: bool = False

@dataclass
class ChartAuditResult:
    """Audit results for a single chart"""
    chart_name: str
    chart_path: str
    version: str
    compliant: bool = False
    score: float = 0.0
    issues: List[ChartIssue] = field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0
    checks_total: int = 0

class ChartAuditor:
    """Audits Helm charts against standards"""

    REQUIRED_FILES = [
        "Chart.yaml",
        "values.yaml",
        "README.md",
        "templates/_helpers.tpl",
        "templates/NOTES.txt",
        "templates/deployment.yaml",  # or statefulset.yaml
        "templates/service.yaml",
        "templates/serviceaccount.yaml",
    ]

    RECOMMENDED_FILES = [
        "values.schema.json",
        "templates/route.yaml",
        "templates/networkpolicy.yaml",
        "tests/test-connection.yaml",
    ]

    OPENSHIFT_GUARDRAILS = [
        "SecurityContextConstraints",  # Should NOT be in app charts
        "ClusterRole",                  # Should NOT be in app charts
        "ClusterRoleBinding",           # Should NOT be in app charts
        "StorageClass",                 # Should NOT be in app charts
    ]

    SECURITY_REQUIREMENTS = {
        "runAsNonRoot": True,
        "allowPrivilegeEscalation": False,
        "privileged": False,
    }

    def __init__(self, base_path: str = "/workspaces/argo-apps"):
        self.base_path = Path(base_path)
        self.charts_path = self.base_path / "charts" / "applications"

    def audit_chart(self, chart_path: Path) -> ChartAuditResult:
        """Audit a single chart"""
        result = ChartAuditResult(
            chart_name=chart_path.name,
            chart_path=str(chart_path),
            version="",
        )

        # Check Chart.yaml
        chart_yaml = chart_path / "Chart.yaml"
        if chart_yaml.exists():
            with open(chart_yaml) as f:
                chart_data = yaml.safe_load(f)
                result.version = chart_data.get("version", "unknown")
        else:
            result.issues.append(ChartIssue(
                severity="error",
                category="structure",
                message="Missing Chart.yaml",
                file="Chart.yaml",
            ))

        # Check required files
        self._check_required_files(chart_path, result)

        # Check recommended files
        self._check_recommended_files(chart_path, result)

        # Check for cluster-scoped resources (OpenShift guardrails)
        self._check_cluster_resources(chart_path, result)

        # Check security context
        self._check_security_context(chart_path, result)

        # Check for Route vs Ingress
        self._check_route_ingress(chart_path, result)

        # Check values.yaml structure
        self._check_values_structure(chart_path, result)

        # Check README documentation
        self._check_readme(chart_path, result)

        # Check for CRDs location
        self._check_crds(chart_path, result)

        # Check _helpers.tpl
        self._check_helpers(chart_path, result)

        # Check for Renovate comments
        self._check_renovate(chart_path, result)

        # Calculate score
        result.checks_total = result.checks_passed + result.checks_failed
        if result.checks_total > 0:
            result.score = (result.checks_passed / result.checks_total) * 100
        result.compliant = result.score >= 80 and result.checks_failed == 0

        return result

    def _check_required_files(self, chart_path: Path, result: ChartAuditResult):
        """Check for required files"""
        for file in self.REQUIRED_FILES:
            file_path = chart_path / file
            # Handle deployment OR statefulset
            if "deployment.yaml" in file:
                deployment_exists = (chart_path / "templates/deployment.yaml").exists()
                statefulset_exists = (chart_path / "templates/statefulset.yaml").exists()
                if deployment_exists or statefulset_exists:
                    result.checks_passed += 1
                else:
                    result.checks_failed += 1
                    result.issues.append(ChartIssue(
                        severity="error",
                        category="structure",
                        message="Missing deployment.yaml or statefulset.yaml",
                        file="templates/",
                    ))
            elif file_path.exists():
                result.checks_passed += 1
            else:
                result.checks_failed += 1
                result.issues.append(ChartIssue(
                    severity="error",
                    category="structure",
                    message=f"Missing required file: {file}",
                    file=file,
                ))

    def _check_recommended_files(self, chart_path: Path, result: ChartAuditResult):
        """Check for recommended files"""
        for file in self.RECOMMENDED_FILES:
            file_path = chart_path / file
            if not file_path.exists():
                result.issues.append(ChartIssue(
                    severity="warning",
                    category="structure",
                    message=f"Recommended file missing: {file}",
                    file=file,
                    fixable=True,
                ))

    def _check_cluster_resources(self, chart_path: Path, result: ChartAuditResult):
        """Check for forbidden cluster-scoped resources"""
        templates_path = chart_path / "templates"
        if not templates_path.exists():
            return

        for template_file in templates_path.glob("*.yaml"):
            if template_file.name.startswith("_"):
                continue

            try:
                with open(template_file) as f:
                    content = f.read()
                    for resource in self.OPENSHIFT_GUARDRAILS:
                        if f"kind: {resource}" in content:
                            result.checks_failed += 1
                            result.issues.append(ChartIssue(
                                severity="error",
                                category="openshift",
                                message=f"Cluster-scoped resource {resource} found in app chart (should be in platform)",
                                file=str(template_file.relative_to(chart_path)),
                            ))
                        else:
                            result.checks_passed += 1
            except Exception as e:
                result.issues.append(ChartIssue(
                    severity="warning",
                    category="structure",
                    message=f"Could not parse {template_file.name}: {e}",
                    file=str(template_file.relative_to(chart_path)),
                ))

    def _check_security_context(self, chart_path: Path, result: ChartAuditResult):
        """Check for OpenShift-compatible security context"""
        deployment_files = [
            chart_path / "templates/deployment.yaml",
            chart_path / "templates/statefulset.yaml",
        ]

        for deployment_file in deployment_files:
            if not deployment_file.exists():
                continue

            try:
                with open(deployment_file) as f:
                    content = f.read()

                    # Check for runAsNonRoot
                    if "runAsNonRoot: true" in content:
                        result.checks_passed += 1
                    else:
                        result.checks_failed += 1
                        result.issues.append(ChartIssue(
                            severity="error",
                            category="security",
                            message="Missing 'runAsNonRoot: true' in securityContext",
                            file=str(deployment_file.relative_to(chart_path)),
                            fixable=True,
                        ))

                    # Check for allowPrivilegeEscalation
                    if "allowPrivilegeEscalation: false" in content:
                        result.checks_passed += 1
                    else:
                        result.checks_failed += 1
                        result.issues.append(ChartIssue(
                            severity="error",
                            category="security",
                            message="Missing 'allowPrivilegeEscalation: false' in securityContext",
                            file=str(deployment_file.relative_to(chart_path)),
                            fixable=True,
                        ))

                    # Check for capabilities drop
                    if "drop:" in content and "ALL" in content:
                        result.checks_passed += 1
                    else:
                        result.checks_failed += 1
                        result.issues.append(ChartIssue(
                            severity="error",
                            category="security",
                            message="Missing 'capabilities.drop: [ALL]' in securityContext",
                            file=str(deployment_file.relative_to(chart_path)),
                            fixable=True,
                        ))

                    # Check for privileged
                    if "privileged: true" in content:
                        result.checks_failed += 1
                        result.issues.append(ChartIssue(
                            severity="error",
                            category="security",
                            message="Privileged containers not allowed on OpenShift",
                            file=str(deployment_file.relative_to(chart_path)),
                        ))
                    else:
                        result.checks_passed += 1

                    # Check for hostPath
                    if "hostPath:" in content:
                        result.checks_failed += 1
                        result.issues.append(ChartIssue(
                            severity="error",
                            category="security",
                            message="hostPath volumes not allowed under restricted SCC",
                            file=str(deployment_file.relative_to(chart_path)),
                        ))
                    else:
                        result.checks_passed += 1

            except Exception as e:
                result.issues.append(ChartIssue(
                    severity="warning",
                    category="security",
                    message=f"Could not parse deployment file: {e}",
                    file=str(deployment_file.relative_to(chart_path)),
                ))

    def _check_route_ingress(self, chart_path: Path, result: ChartAuditResult):
        """Check for Route (preferred) vs Ingress"""
        route_exists = (chart_path / "templates/route.yaml").exists()
        ingress_exists = (chart_path / "templates/ingress.yaml").exists()

        if route_exists:
            result.checks_passed += 1
            result.issues.append(ChartIssue(
                severity="info",
                category="openshift",
                message="Route template found (OpenShift best practice)",
                file="templates/route.yaml",
            ))
        else:
            result.issues.append(ChartIssue(
                severity="warning",
                category="openshift",
                message="No Route template found - consider adding for OpenShift compatibility",
                file="templates/route.yaml",
                fixable=True,
            ))

        if ingress_exists and not route_exists:
            result.issues.append(ChartIssue(
                severity="info",
                category="openshift",
                message="Only Ingress found - consider adding Route as primary with Ingress as fallback",
                file="templates/ingress.yaml",
            ))

    def _check_values_structure(self, chart_path: Path, result: ChartAuditResult):
        """Check values.yaml structure"""
        values_file = chart_path / "values.yaml"
        if not values_file.exists():
            return

        try:
            with open(values_file) as f:
                values = yaml.safe_load(f)

                # Check for required sections
                required_sections = ["image", "service"]
                for section in required_sections:
                    if section in values:
                        result.checks_passed += 1
                    else:
                        result.checks_failed += 1
                        result.issues.append(ChartIssue(
                            severity="error",
                            category="structure",
                            message=f"Missing required section in values.yaml: {section}",
                            file="values.yaml",
                            fixable=True,
                        ))

                # Check for recommended sections
                recommended_sections = ["resources", "securityContext", "serviceAccount"]
                for section in recommended_sections:
                    if section not in values:
                        result.issues.append(ChartIssue(
                            severity="warning",
                            category="structure",
                            message=f"Recommended section missing in values.yaml: {section}",
                            file="values.yaml",
                            fixable=True,
                        ))

        except Exception as e:
            result.issues.append(ChartIssue(
                severity="error",
                category="structure",
                message=f"Could not parse values.yaml: {e}",
                file="values.yaml",
            ))

    def _check_readme(self, chart_path: Path, result: ChartAuditResult):
        """Check README documentation"""
        readme_file = chart_path / "README.md"
        if not readme_file.exists():
            result.checks_failed += 1
            result.issues.append(ChartIssue(
                severity="error",
                category="documentation",
                message="Missing README.md",
                file="README.md",
                fixable=True,
            ))
            return

        try:
            with open(readme_file) as f:
                content = f.read()

                # Check for required sections
                required_sections = ["Prerequisites", "Installation", "Configuration"]
                for section in required_sections:
                    if section in content:
                        result.checks_passed += 1
                    else:
                        result.issues.append(ChartIssue(
                            severity="warning",
                            category="documentation",
                            message=f"README missing recommended section: {section}",
                            file="README.md",
                        ))

        except Exception as e:
            result.issues.append(ChartIssue(
                severity="warning",
                category="documentation",
                message=f"Could not read README.md: {e}",
                file="README.md",
            ))

    def _check_crds(self, chart_path: Path, result: ChartAuditResult):
        """Check CRD location"""
        crds_path = chart_path / "crds"
        templates_path = chart_path / "templates"

        # Check if CRDs are in templates/ instead of crds/
        if templates_path.exists():
            for template_file in templates_path.glob("*.yaml"):
                if "crd" in template_file.name.lower():
                    result.issues.append(ChartIssue(
                        severity="warning",
                        category="structure",
                        message=f"CRD found in templates/ - should be in crds/ directory: {template_file.name}",
                        file=str(template_file.relative_to(chart_path)),
                    ))

        if crds_path.exists() and list(crds_path.glob("*.yaml")):
            result.issues.append(ChartIssue(
                severity="info",
                category="structure",
                message=f"CRDs found in crds/ directory (correct location)",
                file="crds/",
            ))

    def _check_helpers(self, chart_path: Path, result: ChartAuditResult):
        """Check _helpers.tpl"""
        helpers_file = chart_path / "templates/_helpers.tpl"
        if not helpers_file.exists():
            return

        try:
            with open(helpers_file) as f:
                content = f.read()

                # Check for required helper functions
                required_helpers = [
                    "app.name",
                    "app.fullname",
                    "app.labels",
                    "app.selectorLabels",
                ]

                for helper in required_helpers:
                    if helper in content:
                        result.checks_passed += 1
                    else:
                        result.issues.append(ChartIssue(
                            severity="warning",
                            category="structure",
                            message=f"Missing recommended helper function: {helper}",
                            file="templates/_helpers.tpl",
                        ))

        except Exception as e:
            result.issues.append(ChartIssue(
                severity="warning",
                category="structure",
                message=f"Could not parse _helpers.tpl: {e}",
                file="templates/_helpers.tpl",
            ))

    def _check_renovate(self, chart_path: Path, result: ChartAuditResult):
        """Check for Renovate comments on image tags"""
        values_file = chart_path / "values.yaml"
        if not values_file.exists():
            return

        try:
            with open(values_file) as f:
                content = f.read()

                if "renovate:" in content or "# renovate:" in content:
                    result.checks_passed += 1
                    result.issues.append(ChartIssue(
                        severity="info",
                        category="structure",
                        message="Renovate comment found for automated image updates",
                        file="values.yaml",
                    ))
                else:
                    result.issues.append(ChartIssue(
                        severity="warning",
                        category="structure",
                        message="No Renovate comment found - automated image updates disabled",
                        file="values.yaml",
                        fixable=True,
                    ))

        except Exception as e:
            pass

    def audit_domain(self, domain: str) -> List[ChartAuditResult]:
        """Audit all charts in a domain"""
        domain_path = self.charts_path / domain
        if not domain_path.exists():
            print(f"Error: Domain '{domain}' not found at {domain_path}", file=sys.stderr)
            return []

        results = []
        for chart_path in sorted(domain_path.iterdir()):
            if chart_path.is_dir() and (chart_path / "Chart.yaml").exists():
                result = self.audit_chart(chart_path)
                results.append(result)

        return results

    def audit_all(self) -> Dict[str, List[ChartAuditResult]]:
        """Audit all application charts"""
        results = {}

        if not self.charts_path.exists():
            print(f"Error: Charts path not found: {self.charts_path}", file=sys.stderr)
            return results

        for domain_path in sorted(self.charts_path.iterdir()):
            if domain_path.is_dir():
                domain_results = self.audit_domain(domain_path.name)
                if domain_results:
                    results[domain_path.name] = domain_results

        return results


def print_text_report(results: Dict[str, List[ChartAuditResult]]):
    """Print human-readable text report"""
    print("\n" + "="*80)
    print("HELM CHART STANDARDS AUDIT REPORT")
    print("="*80 + "\n")

    total_charts = sum(len(charts) for charts in results.values())
    compliant_charts = sum(
        len([c for c in charts if c.compliant])
        for charts in results.values()
    )

    print(f"Total Charts: {total_charts}")
    print(f"Compliant Charts: {compliant_charts} ({compliant_charts/total_charts*100:.1f}%)")
    print(f"Non-Compliant Charts: {total_charts - compliant_charts}\n")

    for domain, charts in results.items():
        print(f"\n{'='*80}")
        print(f"Domain: {domain}")
        print('='*80)

        for chart in charts:
            status = "✅ COMPLIANT" if chart.compliant else "❌ NON-COMPLIANT"
            print(f"\n{status} | {chart.chart_name} v{chart.version} | Score: {chart.score:.1f}%")
            print(f"  Path: {chart.chart_path}")
            print(f"  Checks: {chart.checks_passed} passed, {chart.checks_failed} failed")

            if chart.issues:
                print(f"\n  Issues ({len(chart.issues)}):")
                for issue in chart.issues:
                    icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}.get(issue.severity, "•")
                    fixable = " [AUTO-FIX AVAILABLE]" if issue.fixable else ""
                    print(f"    {icon} [{issue.severity.upper()}] {issue.message}{fixable}")
                    if issue.file:
                        print(f"       File: {issue.file}")


def print_json_report(results: Dict[str, List[ChartAuditResult]]):
    """Print JSON report"""
    output = {
        "summary": {
            "total_charts": sum(len(charts) for charts in results.values()),
            "compliant_charts": sum(
                len([c for c in charts if c.compliant])
                for charts in results.values()
            ),
        },
        "domains": {}
    }

    for domain, charts in results.items():
        output["domains"][domain] = [
            {
                "name": chart.chart_name,
                "version": chart.version,
                "compliant": chart.compliant,
                "score": chart.score,
                "checks_passed": chart.checks_passed,
                "checks_failed": chart.checks_failed,
                "issues": [
                    {
                        "severity": issue.severity,
                        "category": issue.category,
                        "message": issue.message,
                        "file": issue.file,
                        "fixable": issue.fixable,
                    }
                    for issue in chart.issues
                ]
            }
            for chart in charts
        ]

    print(json.dumps(output, indent=2))


def print_markdown_report(results: Dict[str, List[ChartAuditResult]]):
    """Print markdown report"""
    print("# Helm Chart Standards Audit Report\n")

    total_charts = sum(len(charts) for charts in results.values())
    compliant_charts = sum(
        len([c for c in charts if c.compliant])
        for charts in results.values()
    )

    print("## Summary\n")
    print(f"- **Total Charts:** {total_charts}")
    print(f"- **Compliant:** {compliant_charts} ({compliant_charts/total_charts*100:.1f}%)")
    print(f"- **Non-Compliant:** {total_charts - compliant_charts}\n")

    print("## Compliance by Domain\n")
    print("| Domain | Compliant | Total | Compliance % |")
    print("|--------|-----------|-------|--------------|")

    for domain, charts in results.items():
        domain_compliant = len([c for c in charts if c.compliant])
        domain_total = len(charts)
        compliance_pct = (domain_compliant / domain_total * 100) if domain_total > 0 else 0
        print(f"| {domain} | {domain_compliant} | {domain_total} | {compliance_pct:.1f}% |")

    print("\n## Detailed Results\n")

    for domain, charts in results.items():
        print(f"### {domain}\n")

        for chart in charts:
            status = "✅" if chart.compliant else "❌"
            print(f"#### {status} {chart.chart_name} (v{chart.version})\n")
            print(f"- **Score:** {chart.score:.1f}%")
            print(f"- **Checks Passed:** {chart.checks_passed}")
            print(f"- **Checks Failed:** {chart.checks_failed}\n")

            if chart.issues:
                print("**Issues:**\n")
                for issue in chart.issues:
                    icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}.get(issue.severity, "•")
                    fixable = " *(auto-fix available)*" if issue.fixable else ""
                    print(f"- {icon} **[{issue.severity.upper()}]** {issue.message}{fixable}")
                    if issue.file:
                        print(f"  - File: `{issue.file}`")
                print()


def main():
    parser = argparse.ArgumentParser(description="Audit Helm charts against standards")
    parser.add_argument("--chart", help="Path to single chart to audit")
    parser.add_argument("--domain", help="Domain name to audit (ai, media, etc.)")
    parser.add_argument("--all", action="store_true", help="Audit all charts (default)")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--markdown", action="store_true", help="Output Markdown report")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues (NOT IMPLEMENTED)")

    args = parser.parse_args()

    auditor = ChartAuditor()

    if args.chart:
        chart_path = Path(args.chart)
        result = auditor.audit_chart(chart_path)
        results = {chart_path.parent.name: [result]}
    elif args.domain:
        domain_results = auditor.audit_domain(args.domain)
        results = {args.domain: domain_results}
    else:
        results = auditor.audit_all()

    if args.json:
        print_json_report(results)
    elif args.markdown:
        print_markdown_report(results)
    else:
        print_text_report(results)

    # Exit with error code if any charts are non-compliant
    all_compliant = all(
        chart.compliant
        for charts in results.values()
        for chart in charts
    )
    sys.exit(0 if all_compliant else 1)


if __name__ == "__main__":
    main()
