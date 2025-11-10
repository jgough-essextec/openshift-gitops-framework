---
status: accepted
date: 2025-11-08
decision-makers: ["Platform Engineering Team"]
---

# Use Gatus for Application Health Monitoring

## Context and Problem Statement

With dozens of applications deployed across multiple clusters, we need a way to monitor application health, availability, and performance at a glance. Traditional monitoring solutions (Prometheus/Grafana) focus on metrics, but we need simple up/down status checks with alerting for service availability.

## Decision Drivers

- **Application Focus:** Monitor application endpoints, not just infrastructure
- **Multi-Cluster:** Monitor applications across hub, prod, and test clusters
- **Developer-Friendly:** Health checks defined alongside applications in Git
- **Lightweight:** Minimal resource overhead for home lab environment
- **Dashboard:** Visual status dashboard for quick assessment
- **Alerting:** Notifications when services go down
- **GitOps-Native:** Health checks as code in application charts

## Considered Options

1. **Gatus** - Lightweight health dashboard with alerting
2. **Uptime Kuma** - Self-hosted monitoring tool with UI
3. **Prometheus + Grafana** - Full observability stack
4. **Healthchecks.io** - SaaS monitoring service
5. **Custom Script + Grafana** - Build custom solution

## Decision Outcome

Chosen option: **Gatus**, because:

- **Lightweight:** Single binary, minimal resource usage
- **GitOps-native:** Health checks defined in ConfigMap alongside apps
- **Multi-protocol:** HTTP(S), TCP, DNS, ICMP checks
- **Developer-friendly:** Simple YAML configuration
- **Built-in dashboard:** Clean status page out of the box
- **Alerting:** Multiple notification channels (Discord, Slack, Email, etc.)
- **Open source:** Active development, MIT license

### Consequences

#### Good

- Application health checks defined in Helm chart values
- Single dashboard shows all applications across clusters
- Alerts sent to Discord/Slack when services fail
- Health checks as code (GitOps-managed)
- Lightweight enough for home lab
- Supports external services (TrueNAS, Synology, etc.)

#### Bad

- Additional application to maintain
- Health check configuration separate from app deployment
- Dashboard must be accessible to be useful
- No time-series metrics (just current status)

#### Neutral

- Requires Route/Ingress for dashboard access
- ConfigMap changes require pod restart
- Alert channel credentials managed via External Secrets

## Implementation

### Platform Component

Gatus deployed as platform component in `charts/platform/gatus/`:

- Sync wave 100 (after applications)
- ConfigMap with health checks for all enabled apps
- Dashboard accessible via OpenShift Route
- Alert channels configured per cluster

### Application Pattern

Applications define health checks in values.yaml:

```yaml
gatus:
  enabled: true
  checks:
    - name: app-name
      url: "https://app-name.apps.cluster.example.com"
      interval: 5m
      conditions:
        - "[STATUS] == 200"
        - "[RESPONSE_TIME] < 500"
      alerts:
        - type: discord
```

### Health Check Aggregation

Gatus chart aggregates health checks from all applications:

```yaml
# In Gatus ConfigMap
endpoints:
  {{- range $app := .Values.enabledApps }}
  {{- if $app.gatus.enabled }}
  - name: {{ $app.name }}
    url: {{ $app.gatus.url }}
    conditions: {{ $app.gatus.conditions }}
  {{- end }}
  {{- end }}
```

## Monitoring Strategy

### Check Types

1. **Application Health:** HTTP endpoints with expected status codes
2. **API Health:** REST API endpoints with response validation
3. **Infrastructure:** TrueNAS, Synology, network services
4. **Dependencies:** External services (Cloudflare, Infisical)

### Alert Channels

- **Home lab:** Discord webhook
- **Work lab:** Slack webhook
- **Critical services:** Email + Discord

### Dashboard Access

- **Internal:** OpenShift Route (authenticated users)
- **External:** Optional public status page route

## Links

- **Official Repo:** <https://github.com/TwiN/gatus>
- **Documentation:** <https://gatus.io/>
- **Implementation:** `charts/platform/gatus/`
- **Configuration Guide:** `docs/CONFIGURATION-GUIDE.md`
- **Related ADRs:**
  - [ADR-002: Validated Patterns Framework](0002-validated-patterns-framework-migration.md) - Platform layer
  - [ADR-011: External Secrets Operator](0011-use-external-secrets-operator.md) - Alert credentials
