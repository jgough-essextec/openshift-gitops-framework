#!/usr/bin/env python3
"""
Generate complete application lists for all applicationStacks in values files.
This ensures all available apps are listed (commented out) so users can easily enable/disable them.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent
APPS_DIR = REPO_ROOT / "charts" / "applications"

# Define application metadata
APP_DESCRIPTIONS = {
    # AI Applications
    "litellm": "AI proxy/router for LLM APIs",
    "ollama": "Local LLM inference server",
    "open-webui": "Web interface for Ollama/LiteLLM",

    # Media Applications
    "bazarr": "Subtitle management",
    "flaresolverr": "Cloudflare bypass proxy",
    "gaps": "Missing movie finder for Plex",
    "huntarr": "Bounty manager for *arr apps",
    "jellyfin": "Alternative media server",
    "jellyseerr": "Request management for Jellyfin",
    "kapowarr": "Comic book collection manager",
    "kavita": "Ebook/comic reader",
    "lidarr": "Music collection manager",
    "metube": "YouTube downloader",
    "overseerr": "Request management for Plex/Jellyfin",
    "pinchflat": "YouTube channel archiver",
    "plex": "Media server (primary)",
    "posterizarr": "Poster/artwork management",
    "prowlarr": "Indexer manager",
    "radarr": "Movie collection manager",
    "readarr": "Ebook collection manager",
    "recyclarr": "TRaSH guides sync for *arr apps",
    "sabnzbd": "Usenet downloader",
    "sonarr": "TV series collection manager",
    "tautulli": "Plex monitoring and statistics",

    # Home Automation Applications
    "emqx-operator": "MQTT broker operator",
    "home-assistant": "Home automation platform",
    "node-red": "Flow-based automation",
    "zwavejs2mqtt": "Z-Wave to MQTT bridge",

    # Productivity Applications
    "bookmarks": "Bookmark manager",
    "cyberchef": "Data transformation tool",
    "excalidraw": "Collaborative whiteboard",
    "it-tools": "Developer utilities collection",
    "startpunkt": "Customizable startpage",
    "terraform-enterprise": "Terraform private registry",

    # Infrastructure Applications
    "adsb": "Aircraft tracking (FlightAware/ADS-B)",
    "glue-worker": "Custom Python automation workers",
    "paperless-ai": "AI-powered document processing",
    "paperless-gpt": "GPT integration for Paperless",
    "paperless-ngx": "Document management system",
}

def get_apps_in_domain(domain: str) -> list:
    """Get list of app directories in a domain, excluding special directories"""
    domain_dir = APPS_DIR / domain
    if not domain_dir.exists():
        return []

    apps = []
    for item in sorted(domain_dir.iterdir()):
        if item.is_dir() and item.name not in ["templates", "Chart.yaml"]:
            apps.append(item.name)

    return apps

def generate_app_list(domain: str, enabled_apps: list = None, indent: int = 8) -> str:
    """Generate formatted app list with descriptions"""
    if enabled_apps is None:
        enabled_apps = []

    apps = get_apps_in_domain(domain)
    if not apps:
        return ""

    lines = []
    indent_str = " " * indent

    # Add enabled apps first (uncommented)
    if enabled_apps:
        lines.append(f"{indent_str}# Active Apps")
        for app in enabled_apps:
            if app in apps:
                desc = APP_DESCRIPTIONS.get(app, "")
                if desc:
                    lines.append(f"{indent_str}- {app:<20} # {desc}")
                else:
                    lines.append(f"{indent_str}- {app}")
        lines.append("")

    # Add all available apps (commented if not enabled)
    available_apps = [a for a in apps if a not in enabled_apps]
    if available_apps:
        if enabled_apps:
            lines.append(f"{indent_str}# Available Apps (commented = disabled)")
        for app in available_apps:
            desc = APP_DESCRIPTIONS.get(app, "")
            if desc:
                lines.append(f"{indent_str}# - {app:<18} # {desc}")
            else:
                lines.append(f"{indent_str}# - {app}")

    return "\n".join(lines)

def main():
    """Generate complete app list template"""
    domains = {
        "ai": "AI / ML Applications",
        "media": "Media Management Applications",
        "home-automation": "Home Automation Applications",
        "productivity": "Productivity Applications",
        "infrastructure": "Infrastructure Applications",
    }

    print("# Application Stacks Template")
    print("# Copy this section into your values-<cluster>.yaml file")
    print()
    print("  applicationStacks:")

    for domain, title in domains.items():
        print(f"    # {title}")
        domain_key = domain.replace("-", "")  # home-automation → homeAutomation
        if domain == "home-automation":
            domain_key = "homeAutomation"

        print(f"    {domain_key}:")
        print(f"      enabled: false")
        print(f"      apps:")

        app_list = generate_app_list(domain)
        if app_list:
            print(app_list)
        else:
            print("        # No apps available")
        print()

if __name__ == "__main__":
    main()
