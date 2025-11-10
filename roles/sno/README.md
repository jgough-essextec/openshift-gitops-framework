# Validated Patterns Cluster Bootstrap

This chart deploys the master ApplicationSets for a cluster using the Validated Patterns framework.

## Structure

This chart replaces individual ApplicationSet templates with Applications that deploy master ApplicationSets:

- **Platform ApplicationSet**: Deploys platform components (ESO, certificates, VPA, storage, etc.)
- **Application ApplicationSets**: Deploy user applications by domain (ai, media, home-automation, productivity)
- **Topology ApplicationSets** (future): Deploy topology-specific components

## Usage

Deploy this chart as the "cluster" Application in bootstrap:

```bash
helm template sno ./roles/sno \
  -f values-global.yaml \
  -f clusters/individual-clusters/values-prod.yaml \
  -f values-secret.yaml
```

The chart creates Applications that deploy Helm charts containing ApplicationSets, which then create the final Applications for each component/app.

## Values

Values follow the Validated Patterns structure:

```yaml
clusterGroup:
  name: sno
  platformComponents:
    # ... enabled/disabled flags
  storage:
    # ... storage configuration
  applicationStacks:
    ai:
      enabled: true
      apps: [litellm, open-webui]
    # ... other stacks
```

See `values-*.yaml` in repo root for complete examples.
