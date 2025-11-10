# Application Inventory Update - Values Files

## Overview

Updated all `values-*.yaml` files to include complete application inventories across all five domains. This provides visibility and easy management of all 38 available applications through simple enable/disable via comments.

## Changes Made

### Pattern

All `applicationStacks` sections were updated with:

1. **Complete app listings:** All 38 apps listed across 5 domains
2. **Descriptive comments:** Each app includes a brief description
3. **Enable/disable via comments:** Uncommented = enabled, commented = disabled
4. **Domain organization:** Apps grouped by functional area

### Application Inventory

Total: **38 applications** across **5 domains**

#### AI / ML Applications (3)

- `litellm` - AI proxy/router for LLM APIs
- `ollama` - Local LLM inference server
- `open-webui` - Web interface for Ollama/LiteLLM

#### Media Management Applications (21)

- `bazarr` - Subtitle management
- `flaresolverr` - Cloudflare bypass proxy
- `gaps` - Missing movie finder for Plex
- `huntarr` - Bounty manager for \*arr apps
- `jellyfin` - Alternative media server
- `jellyseerr` - Request management for Jellyfin
- `kapowarr` - Comic book collection manager
- `kavita` - Ebook/comic reader
- `lidarr` - Music collection manager
- `metube` - YouTube downloader
- `overseerr` - Request management for Plex/Jellyfin
- `pinchflat` - YouTube channel archiver
- `plex` - Media server (primary)
- `posterizarr` - Poster/artwork management
- `prowlarr` - Indexer manager
- `radarr` - Movie collection manager
- `readarr` - Ebook collection manager
- `recyclarr` - TRaSH guides sync for \*arr apps
- `sabnzbd` - Usenet downloader
- `sonarr` - TV series collection manager
- `tautulli` - Plex monitoring and statistics

#### Home Automation Applications (4)

- `emqx-operator` - MQTT broker operator
- `home-assistant` - Home automation platform
- `node-red` - Flow-based automation
- `zwavejs2mqtt` - Z-Wave to MQTT bridge

#### Productivity Applications (6)

- `bookmarks` - Bookmark manager
- `cyberchef` - Data transformation tool
- `excalidraw` - Collaborative whiteboard
- `it-tools` - Developer utilities collection
- `startpunkt` - Customizable startpage
- `terraform-enterprise` - Terraform private registry

#### Infrastructure Applications (5)

- `adsb` - Aircraft tracking (FlightAware/ADS-B)
- `glue-worker` - Custom Python automation workers
- `paperless-ai` - AI-powered document processing
- `paperless-gpt` - GPT integration for Paperless
- `paperless-ngx` - Document management system

## Files Updated

### Cluster Values Files

- ✅ `values-prod.yaml` - Production cluster (SNO topology)
- ✅ `values-test.yaml` - Test/dev cluster
- ✅ `values-hub.yaml` - Management/hub cluster

### Topology Values Files

- ✅ `values-compact.yaml` - 3-node compact topology
- ✅ `values-full.yaml` - 6+ node full HA topology

### Cluster Set Values Files

- ✅ `values-home.yaml` - Home cluster set defaults
- ✅ `values-worklab.yaml` - Work lab cluster set defaults
- ✅ `values-cloud.yaml` - Cloud cluster set defaults

### Global Values File

- ✅ `values-global.yaml` - Pattern-wide defaults

## Example Structure

```yaml
applicationStacks:
  # AI / ML Applications
  ai:
    enabled: true # Enable entire domain
    apps:
      # Active Apps
      - ollama # Local LLM inference server
      - open-webui # Web interface for Ollama/LiteLLM

      # Available Apps (commented = disabled)
      # - litellm        # AI proxy/router for LLM APIs

  # Media Management Applications
  media:
    enabled: true
    apps:
      # Active Apps
      - plex # Media server (primary)
      - sonarr # TV series collection manager
      - radarr # Movie collection manager


      # Available Apps (commented = disabled)
      # - bazarr         # Subtitle management
      # - overseerr      # Request management for Plex/Jellyfin
      # ... (remaining media apps)
```

## Usage

### Enable an Application

1. Locate the app in the appropriate domain
2. Uncomment the line (remove `# ` prefix)
3. Commit and push - Argo CD will deploy

```yaml
apps:
  - plex               # Already enabled
  # - overseerr        # Currently disabled

# To enable overseerr, change to:
apps:
  - plex
  - overseerr          # Now enabled
```

### Disable an Application

1. Locate the enabled app
2. Comment the line (add `# ` prefix)
3. Commit and push - Argo CD will prune

```yaml
apps:
  - plex
  - overseerr          # Currently enabled

# To disable overseerr, change to:
apps:
  - plex
  # - overseerr        # Now disabled
```

### Enable Entire Domain

Set `enabled: true` for the domain and uncomment desired apps:

```yaml
media:
  enabled: true # Enable media domain
  apps:
    - plex
    - sonarr
    - radarr
    # ... other apps remain commented
```

### Disable Entire Domain

Set `enabled: false` to disable all apps in the domain regardless of app list:

```yaml
media:
  enabled: false # Disables entire domain
  apps:
    - plex # Will NOT deploy
    - sonarr # Will NOT deploy
```

## Benefits

1. **Visibility:** All available apps visible in values files
2. **Discoverability:** Users can see what apps exist without browsing chart directories
3. **Easy Management:** Simple comment/uncomment to enable/disable
4. **Documentation:** App descriptions inline with configuration
5. **Consistency:** Same structure across all values files
6. **Version Control:** Git history shows exactly which apps changed

## Scripts

### Generate Template

Use `scripts/generate-app-list-template.py` to generate a fresh template:

```bash
python3 scripts/generate-app-list-template.py > app-inventory.txt
```

This generates a complete listing of all apps with descriptions that can be copied into values files.

## Related Documentation

- [Values Hierarchy](VALUES-HIERARCHY.md) - Multi-layer configuration structure
- [Chart Standards](CHART-STANDARDS.md) - Application chart requirements
- [Adding Applications Checklist](.github/instructions/adding-an-application-checklist.md) - New app workflow
- [Copilot Instructions](.github/copilot-instructions.md) - AI assistant guidance

## Notes

- Apps are commented by default in all values files except specific clusters where they're actively used
- Cluster-specific values override cluster-set values override global values
- The `enabled` flag at the domain level controls whether ANY apps in that domain can deploy
- Individual app enable/disable (via comments) only works when domain `enabled: true`
