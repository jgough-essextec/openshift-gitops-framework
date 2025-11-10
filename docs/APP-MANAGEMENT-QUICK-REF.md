# Application Management Quick Reference

## Complete Application Inventory (38 Apps)

All values-\*.yaml files now contain complete application inventories for easy enable/disable.

### Application Domains

| Domain              | Apps | Location                               |
| ------------------- | ---- | -------------------------------------- |
| **AI / ML**         | 3    | `charts/applications/ai/`              |
| **Media**           | 21   | `charts/applications/media/`           |
| **Home Automation** | 4    | `charts/applications/home-automation/` |
| **Productivity**    | 6    | `charts/applications/productivity/`    |
| **Infrastructure**  | 5    | `charts/applications/infrastructure/`  |

### Quick Actions

#### Enable an App

Edit `values-<cluster>.yaml` and uncomment the app:

```yaml
apps:
  # - litellm          # Disabled (commented)
  - ollama # Enabled (uncommented)
```

#### Disable an App

Edit `values-<cluster>.yaml` and comment the app:

```yaml
apps:
  - ollama # Currently enabled
  # Change to:
  # - ollama           # Now disabled
```

#### Enable Entire Domain

```yaml
media:
  enabled: true # Enable domain
  apps:
    - plex # Uncomment desired apps
    - sonarr
```

#### Disable Entire Domain

```yaml
media:
  enabled: false # Domain disabled (apps ignored)
```

### Available Applications

<details>
<summary><b>AI / ML (3 apps)</b></summary>

- `litellm` - AI proxy/router for LLM APIs
- `ollama` - Local LLM inference server
- `open-webui` - Web interface for Ollama/LiteLLM

</details>

<details>
<summary><b>Media (21 apps)</b></summary>

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

</details>

<details>
<summary><b>Home Automation (4 apps)</b></summary>

- `emqx-operator` - MQTT broker operator
- `home-assistant` - Home automation platform
- `node-red` - Flow-based automation
- `zwavejs2mqtt` - Z-Wave to MQTT bridge

</details>

<details>
<summary><b>Productivity (6 apps)</b></summary>

- `bookmarks` - Bookmark manager
- `cyberchef` - Data transformation tool
- `excalidraw` - Collaborative whiteboard
- `it-tools` - Developer utilities collection
- `startpunkt` - Customizable startpage
- `terraform-enterprise` - Terraform private registry

</details>

<details>
<summary><b>Infrastructure (5 apps)</b></summary>

- `adsb` - Aircraft tracking (FlightAware/ADS-B)
- `glue-worker` - Custom Python automation workers
- `paperless-ai` - AI-powered document processing
- `paperless-gpt` - GPT integration for Paperless
- `paperless-ngx` - Document management system

</details>

### Helper Scripts

#### Generate App List Template

```bash
python3 scripts/generate-app-list-template.py
```

Generates formatted YAML with all apps and descriptions.

#### Verify App Inventory

```bash
scripts/verify-app-inventory.sh
```

Validates all values files have correct app counts per domain.

### Documentation

- [Full Implementation Details](docs/app-inventory-implementation-summary.md)
- [Values Update Guide](docs/values-app-inventory-update.md)
- [Values Hierarchy](docs/VALUES-HIERARCHY.md)

---

**Note:** All apps are commented (disabled) by default in all values files. Uncomment to enable per cluster.
