#!/usr/bin/env python3
"""
Generate comprehensive indices for OpenShift-Arch repository.

This script auto-generates index files for:
- ADRs (Architecture Decision Records)
- Blueprints
- Presentations
- Components
- Shared resources
- Client documentation

Usage:
    python scripts/generate_indices.py
    python scripts/generate_indices.py --check  # Validation mode (CI/CD)
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


class IndexGenerator:
    """Generate indices for various documentation types."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: List[str] = []

    def generate_adr_index(self) -> str:
        """Generate ADR index with metadata."""
        adr_dir = self.repo_root / "docs/decisions"
        adrs = []

        for adr_file in sorted(adr_dir.glob("*.md")):
            if adr_file.name == "template.md":
                continue

            content = adr_file.read_text(encoding="utf-8")
            metadata = self._extract_yaml_metadata(content)
            title = self._extract_title(content)
            number = self._extract_adr_number(adr_file.name)

            adrs.append({
                "number": number,
                "file": adr_file.name,
                "title": title,
                "status": metadata.get("status", "unknown"),
                "date": metadata.get("date", "unknown"),
            })

        # Group by status
        by_status: Dict[str, List[Dict]] = {
            "accepted": [],
            "proposed": [],
            "deprecated": [],
            "superseded": [],
        }

        for adr in adrs:
            status = adr["status"]
            if status in by_status:
                by_status[status].append(adr)
            else:
                by_status.setdefault("other", []).append(adr)

        # Generate markdown
        lines = [
            "# Architecture Decision Records (ADRs)",
            "",
            "Architectural decisions for the OpenShift platform.",
            "",
            "---",
            "",
            "## Index by Status",
            "",
        ]

        for status in ["accepted", "proposed", "deprecated", "superseded", "other"]:
            if status not in by_status or not by_status[status]:
                continue

            lines.append(f"### {status.title()}")
            lines.append("")

            for adr in sorted(by_status[status], key=lambda x: x["number"]):
                lines.append(
                    f"- [{adr['number']:03d}: {adr['title']}](docs/decisions/{adr['file']}) "
                    f"*({adr['date']})*"
                )

            lines.append("")

        # Add chronological list
        lines.extend([
            "---",
            "",
            "## Chronological List",
            "",
        ])

        for adr in sorted(adrs, key=lambda x: x["number"]):
            lines.append(
                f"{adr['number']:03d}. [{adr['title']}](docs/decisions/{adr['file']}) "
                f"- **{adr['status']}** *({adr['date']})*"
            )

        lines.extend([
            "",
            "---",
            "",
            f"*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            "*Total ADRs:* {}".format(len(adrs)),
        ])

        return "\n".join(lines)

    def generate_blueprint_index(self) -> str:
        """Generate blueprint documentation index."""
        blueprint_dir = self.repo_root / "blueprints"
        blueprints = []

        if blueprint_dir.exists():
            for bp_file in sorted(blueprint_dir.glob("*.md")):
                content = bp_file.read_text(encoding="utf-8")
                title = self._extract_title(content)
                summary = self._extract_summary(content)

                blueprints.append({
                    "file": bp_file.name,
                    "title": title,
                    "summary": summary,
                })

        lines = [
            "# OpenShift Blueprints",
            "",
            "Comprehensive blueprints and deployment patterns for OpenShift.",
            "",
            "---",
            "",
        ]

        for bp in blueprints:
            lines.append(f"## [{bp['title']}](blueprints/{bp['file']})")
            lines.append("")
            if bp["summary"]:
                lines.append(bp["summary"])
                lines.append("")

        lines.extend([
            "---",
            "",
            f"*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])

        return "\n".join(lines)

    def generate_presentation_index(self) -> str:
        """Generate presentations index."""
        pres_dir = self.repo_root / "docs" / "presentations"
        
        templates = []
        examples = []

        if (pres_dir / "templates").exists():
            for template in sorted((pres_dir / "templates").glob("*.md")):
                content = template.read_text(encoding="utf-8")
                title = self._extract_title(content)
                templates.append({"file": template.name, "title": title})

        if (pres_dir / "examples").exists():
            for example in sorted((pres_dir / "examples").glob("*.md")):
                content = example.read_text(encoding="utf-8")
                title = self._extract_title(content)
                examples.append({"file": example.name, "title": title})

        lines = [
            "# Presentation Resources",
            "",
            "Templates and examples for creating client presentations.",
            "",
            "---",
            "",
            "## Templates",
            "",
        ]

        for template in templates:
            lines.append(f"- [{template['title']}](presentations/templates/{template['file']})")

        lines.extend([
            "",
            "## Examples",
            "",
        ])

        for example in examples:
            lines.append(f"- [{example['title']}](presentations/examples/{example['file']})")

        lines.extend([
            "",
            "---",
            "",
            "## Usage",
            "",
            "1. Select appropriate template based on audience and purpose",
            "2. Copy template to client-specific presentations directory",
            "3. Customize with client context and content",
            "4. Use export utilities to generate PowerPoint/PDF",
            "",
            "---",
            "",
            f"*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])

        return "\n".join(lines)

    def generate_component_index(self) -> str:
        """Generate components index."""
        comp_dir = self.repo_root / "docs" / "architecture" / "components"
        
        components = []

        if comp_dir.exists():
            for comp_file in sorted(comp_dir.glob("*.md")):
                if comp_file.name == "README.md":
                    continue
                    
                content = comp_file.read_text(encoding="utf-8")
                title = self._extract_title(content)
                summary = self._extract_summary(content)

                components.append({
                    "file": comp_file.name,
                    "title": title,
                    "summary": summary,
                })

        lines = [
            "# OpenShift Components",
            "",
            "Component breakdown by architectural planes.",
            "",
            "---",
            "",
        ]

        for comp in components:
            lines.append(f"## [{comp['title']}](architecture/components/{comp['file']})")
            lines.append("")
            if comp["summary"]:
                lines.append(comp["summary"])
                lines.append("")

        lines.extend([
            "---",
            "",
            "## Related Documentation",
            "",
            "- [Architecture Taxonomy](architecture/taxonomy.md)",
            "- [API Design Patterns](architecture/api/)",
            "- [OpenShift Deployment Blueprint](../blueprints/OpenShift_Deployment_Solutions_Blueprint.md)",
            "",
            "---",
            "",
            f"*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])

        return "\n".join(lines)

    def generate_shared_index(self) -> str:
        """Generate shared resources index."""
        shared_dir = self.repo_root / "shared"
        
        resources = []

        if shared_dir.exists():
            for resource_dir in sorted(shared_dir.iterdir()):
                if not resource_dir.is_dir():
                    continue
                    
                readme = resource_dir / "README.md"
                if readme.exists():
                    content = readme.read_text(encoding="utf-8")
                    title = self._extract_title(content)
                    summary = self._extract_summary(content)

                    resources.append({
                        "dir": resource_dir.name,
                        "title": title,
                        "summary": summary,
                    })

        lines = [
            "# Shared Resources",
            "",
            "Reusable patterns, automation, and operational guides.",
            "",
            "---",
            "",
        ]

        for resource in resources:
            lines.append(f"## [{resource['title']}](shared/{resource['dir']}/)")
            lines.append("")
            if resource["summary"]:
                lines.append(resource["summary"])
                lines.append("")

        lines.extend([
            "---",
            "",
            f"*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])

        return "\n".join(lines)

    def generate_client_index(self) -> str:
        """Generate clients index."""
        client_dir = self.repo_root / "client"
        
        clients = []

        if client_dir.exists():
            for client_subdir in sorted(client_dir.iterdir()):
                if not client_subdir.is_dir():
                    continue
                    
                readme = client_subdir / "README.md"
                strategy = client_subdir / "1-Strategy" / "README.md"
                
                if readme.exists():
                    content = readme.read_text(encoding="utf-8")
                    title = self._extract_title(content) or client_subdir.name
                    summary = self._extract_summary(content)
                elif strategy.exists():
                    content = strategy.read_text(encoding="utf-8")
                    title = client_subdir.name
                    summary = self._extract_summary(content)
                else:
                    title = client_subdir.name
                    summary = None

                clients.append({
                    "dir": client_subdir.name,
                    "title": title,
                    "summary": summary,
                })

        lines = [
            "# Client Documentation",
            "",
            "Client-specific architecture and implementation documentation.",
            "",
            "---",
            "",
        ]

        if clients:
            for client in clients:
                lines.append(f"## [{client['title']}](client/{client['dir']}/)")
                lines.append("")
                if client["summary"]:
                    lines.append(client["summary"])
                    lines.append("")
        else:
            lines.append("*No client documentation yet.*")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Creating New Client Documentation",
            "",
            "Use the [Client Architecture Template](docs/templates/CLIENT_ARCHITECTURE_TEMPLATE.md) "
            "to create standardized client documentation.",
            "",
            "---",
            "",
            f"*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])

        return "\n".join(lines)

    def _extract_yaml_metadata(self, content: str) -> Dict:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                return {}
        return {}

    def _extract_title(self, content: str) -> str:
        """Extract first H1 title from markdown."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else "Untitled"

    def _extract_summary(self, content: str) -> str:
        """Extract first paragraph after title as summary."""
        # Remove YAML frontmatter
        content = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
        
        # Find first paragraph after title
        match = re.search(r"^#\s+.+$\s*\n\s*\n(.+?)(?:\n\n|\n##)", content, re.MULTILINE | re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # Limit to first sentence or 200 chars
            summary = re.split(r"[.!?]\s", summary)[0]
            if len(summary) > 200:
                summary = summary[:197] + "..."
            return summary
        return ""

    def _extract_adr_number(self, filename: str) -> int:
        """Extract ADR number from filename."""
        match = re.match(r"(\d+)-", filename)
        return int(match.group(1)) if match else 0

    def write_index(self, index_name: str, content: str, output_path: Path) -> bool:
        """Write index to file."""
        try:
            output_path.write_text(content, encoding="utf-8")
            print(f"✅ Generated {index_name}: {output_path}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to write {index_name}: {e}")
            print(f"❌ Failed to generate {index_name}: {e}")
            return False

    def check_index(self, index_name: str, content: str, output_path: Path) -> bool:
        """Check if index is up to date (for CI/CD)."""
        if not output_path.exists():
            self.errors.append(f"{index_name} does not exist: {output_path}")
            return False

        existing = output_path.read_text(encoding="utf-8")
        
        # Compare without timestamps
        existing_no_ts = re.sub(r"\*Generated:.*", "", existing)
        new_no_ts = re.sub(r"\*Generated:.*", "", content)

        if existing_no_ts.strip() != new_no_ts.strip():
            self.errors.append(f"{index_name} is out of date: {output_path}")
            return False

        print(f"✅ {index_name} is up to date: {output_path}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Generate repository indices")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if indices are up to date (CI mode)"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Repository root directory"
    )
    args = parser.parse_args()

    generator = IndexGenerator(args.repo_root)

    indices = [
        ("ADR Index", generator.generate_adr_index, args.repo_root / "adr-index.md"),
        ("Blueprint Index", generator.generate_blueprint_index, args.repo_root / "docs" / "indices" / "blueprints.md"),
        ("Presentation Index", generator.generate_presentation_index, args.repo_root / "docs" / "indices" / "presentations.md"),
        ("Component Index", generator.generate_component_index, args.repo_root / "docs" / "indices" / "components.md"),
        ("Shared Resources Index", generator.generate_shared_index, args.repo_root / "docs" / "indices" / "shared.md"),
        ("Client Index", generator.generate_client_index, args.repo_root / "docs" / "indices" / "clients.md"),
    ]

    # Ensure indices directory exists
    indices_dir = args.repo_root / "docs" / "indices"
    indices_dir.mkdir(parents=True, exist_ok=True)

    success = True
    for name, generator_func, output_path in indices:
        content = generator_func()
        
        if args.check:
            if not generator.check_index(name, content, output_path):
                success = False
        else:
            if not generator.write_index(name, content, output_path):
                success = False

    if not success:
        print("\n❌ Index generation failed with errors:")
        for error in generator.errors:
            print(f"  - {error}")
        
        if args.check:
            print("\n💡 Run 'python scripts/generate_indices.py' to update indices")
        
        sys.exit(1)

    print(f"\n✅ All indices {'validated' if args.check else 'generated'} successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()
