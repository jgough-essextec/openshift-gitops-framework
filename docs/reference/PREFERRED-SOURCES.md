# Preferred Application Sources

This document defines the preferred sources and priorities when adding new applications to the argo-apps repository.

---

## 🚀 Quick Reference Card

**When adding a new application, search in this order:**

1. **🥇 [OperatorHub.io](https://operatorhub.io/)** - Search for Kubernetes operators (OLM)
   - Priority: Red Hat Certified > Certified Partners > Community
2. **🥈 [ArtifactHub.io](https://artifacthub.io/)** - Search for Helm charts & operators
   - Priority: Official > Verified Publisher > CNCF > Community
3. **🥉 [Quay.io](https://quay.io/)** - Container registry (Red Hat/OpenShift focused)
   - Priority: Official > Verified > Community
4. **🏅 [Docker Hub](https://hub.docker.com/)** - Container registry (general purpose)
   - Priority: Official Images > Verified Publishers > Community

**Golden Rules:**

- ✅ **Operators > Helm Charts > Custom Deployments**
- ✅ **Official > Verified > CNCF > Community**
- ✅ **OLM > Operator Helm Chart > Direct Install**

**Quick Search Pattern:**

```bash
# 1. Check for operator
https://operatorhub.io/?keyword=<app-name>

# 2. Check for Helm chart
https://artifacthub.io/packages/search?ts_query_web=<app-name>

# 3. Check for official image
https://quay.io/search?q=<app-name>
https://hub.docker.com/search?q=<app-name>
```

---

## 🎯 Priority Order

When searching for application charts, images, and operators, follow this priority order:

### 1. **Operators First (Highest Priority)**

Prefer Kubernetes operators over standalone deployments. Operators provide:

- Automated lifecycle management
- Self-healing capabilities
- Upgrade automation
- Best practices built-in

**Operator Priorities:**

1. **OperatorHub (OLM)** - Operator Lifecycle Manager catalogs

   - Red Hat Certified Operators
   - Red Hat Marketplace
   - Certified Partners
   - Community Operators

2. **Operator Helm Charts** - Official operator Helm charts

   - Chart must deploy the operator, not just CRs

3. **Direct Operator Installation** - Operator SDK or manifest-based
   - Official GitHub releases
   - Vendor-provided manifests

### 2. **Helm Charts (Secondary Priority)**

If no operator exists, prefer official Helm charts:

1. **Official Charts** - Maintained by project authors
2. **Verified Charts** - Verified publishers on ArtifactHub
3. **CNCF Charts** - Cloud Native Computing Foundation projects
4. **Community Charts** - Well-maintained community charts

### 3. **Container Images (Lowest Priority)**

Only build custom Deployments if no operator or Helm chart exists:

1. **Official Images** - Project-maintained images
2. **Verified Publishers** - Verified on registries
3. **CNCF Images** - Cloud Native Computing Foundation
4. **Community Images** - Well-maintained, regularly updated

---

## 📦 Repository Sources

### Primary Sources

#### 1. ArtifactHub (https://artifacthub.io/)

**Best for:** Discovering Helm charts, operators, and OLM packages

**Search Strategy:**

```
1. Search by application name
2. Filter by "Official" or "Verified Publisher"
3. Check repository stars, last update date
4. Verify OpenShift compatibility
5. Review security scanning results
```

**Example Search:**

```
https://artifacthub.io/packages/search?ts_query_web=plex&sort=relevance&page=1
```

**Filters to Use:**

- ✅ Official repository
- ✅ Verified publisher
- ✅ Recently updated (< 3 months)
- ✅ Security scanning passed
- ✅ Has README and values documentation

#### 2. OperatorHub.io (https://operatorhub.io/)

**Best for:** Kubernetes operators

**Categories:**

- **Red Hat Certified** - Production-ready, supported operators
- **Certified Partners** - Verified partner operators
- **Community** - Community-maintained operators

**Example Search:**

```
https://operatorhub.io/?keyword=metallb
```

**Evaluation Criteria:**

- Operator maturity level (Seamless Upgrades > Full Lifecycle > Basic Install)
- CRD capabilities
- Update frequency
- Documentation quality
- OpenShift support

#### 3. Quay.io (https://quay.io/)

**Best for:** Container images, especially Red Hat/OpenShift focused

**Search Strategy:**

```
1. Search by image name
2. Check "Official" or "Verified" badges
3. Review security scanning results
4. Check multi-arch support (amd64, arm64)
5. Verify regular updates
```

**Example:**

```
https://quay.io/repository/prometheus/prometheus
```

**Preferred Namespaces:**

- `redhat/` - Red Hat official images
- `openshift/` - OpenShift components
- `projectname/` - Official project images

#### 4. Docker Hub (https://hub.docker.com/)

**Best for:** Wide variety of images, community projects

**Search Strategy:**

```
1. Search by image name
2. Filter by "Official Image" or "Verified Publisher"
3. Check pull counts and stars
4. Review Dockerfile (if available)
5. Check update frequency
```

**Example:**

```
https://hub.docker.com/_/postgres
```

**Verified Publishers:**

- Look for blue checkmark badge
- Check "Official Image" designation
- Review security scan results

### Secondary Sources

#### 5. GitHub Container Registry (ghcr.io)

**Best for:** Modern projects, GitHub-native builds

**Example:**

```
ghcr.io/home-assistant/home-assistant
```

#### 6. Google Container Registry (gcr.io)

**Best for:** Google Cloud and Kubernetes ecosystem projects

**Example:**

```
gcr.io/google-samples/hello-app
```

---

## 🔍 Evaluation Checklist

Before adding any application, verify:

### Operator Discovery

- [ ] Search OperatorHub.io for Kubernetes operator
- [ ] Check operator maturity level
- [ ] Verify OpenShift compatibility
- [ ] Review CRD capabilities
- [ ] Check documentation completeness

### Chart Discovery

- [ ] Search ArtifactHub for official/verified charts
- [ ] Check chart version and app version
- [ ] Review values.yaml for configurability
- [ ] Verify OpenShift compatibility (Route support, SCC compliance)
- [ ] Check recent update activity (< 3 months ideal)

### Image Discovery

- [ ] Verify official/verified publisher status
- [ ] Check multi-architecture support
- [ ] Review security scan results (no critical CVEs)
- [ ] Verify regular update cadence
- [ ] Check documentation and examples

### Security & Compliance

- [ ] Image scanned for vulnerabilities
- [ ] Runs with restricted SCC (runAsNonRoot, no privilege escalation)
- [ ] No hardcoded secrets or credentials
- [ ] Uses external-secrets-operator for sensitive data
- [ ] HTTPS/TLS enabled by default

### License Compliance

- [ ] Open source license (Apache, MIT, GPL, etc.)
- [ ] License compatible with organizational policies
- [ ] No commercial/proprietary restrictions
- [ ] Clear attribution requirements

---

## 🎨 Chart Selection Criteria

### When Multiple Options Exist

If you find multiple charts/operators, choose based on:

1. **Official > Verified > Community**

   - Official from project maintainers (best)
   - Verified publishers (good)
   - Community charts (acceptable if well-maintained)

2. **Operator > Helm > Custom**

   - Prefer operators for complex applications
   - Use Helm for simpler deployments
   - Build custom only when necessary

3. **OpenShift Native > Generic Kubernetes**

   - Supports OpenShift Routes
   - Uses SecurityContextConstraints
   - Integrates with OpenShift Console
   - Validated on OpenShift

4. **Recent Updates > Stale**

   - Updated within 3 months (excellent)
   - Updated within 6 months (good)
   - Updated within 1 year (acceptable)
   - Older than 1 year (investigate alternatives)

5. **Documented > Undocumented**

   - Complete README
   - Values documentation
   - Architecture diagrams
   - Example configurations

6. **Scanned > Unscanned**
   - Security scanning enabled
   - No critical vulnerabilities
   - Regular vulnerability patches
   - Automated scanning in CI

---

## 📋 Search Workflow

### Step 1: Check for Operator

```bash
# Search OperatorHub
1. Visit https://operatorhub.io/
2. Search for application name
3. Filter by "Red Hat Certified" or "Certified Partners"
4. Check maturity level and capabilities
```

### Step 2: Search Helm Charts

```bash
# Search ArtifactHub
1. Visit https://artifacthub.io/
2. Search for application name
3. Filter by package kind: "Helm" or "OLM"
4. Filter by "Official" or "Verified Publisher"
5. Sort by relevance or stars
```

### Step 3: Find Container Images

```bash
# Search Quay.io
1. Visit https://quay.io/
2. Search for application name
3. Check for official/verified badges
4. Review security scan results

# Search Docker Hub
1. Visit https://hub.docker.com/
2. Search for application name
3. Filter by "Official Image" or "Verified Publisher"
4. Check pull count and last update
```

### Step 4: Evaluate Options

```bash
# Compare findings
1. List all discovered options
2. Apply priority order (Operator > Helm > Image)
3. Apply quality criteria (Official > Verified > Community)
4. Check OpenShift compatibility
5. Document choice in PR description
```

---

## 🏷️ Registry Preferences

### By Use Case

| Use Case             | Preferred Registry | Reason                       |
| -------------------- | ------------------ | ---------------------------- |
| OpenShift native     | Quay.io (Red Hat)  | Official OpenShift ecosystem |
| Kubernetes operators | OperatorHub.io     | Operator-specific discovery  |
| General purpose      | Docker Hub         | Widest selection             |
| GitHub projects      | ghcr.io            | Native to GitHub             |
| Cloud-native         | gcr.io or Quay.io  | CNCF ecosystem               |

### Registry Priority Order

1. **Quay.io** (Red Hat Official)
2. **Docker Hub Official Images**
3. **GitHub Container Registry** (ghcr.io)
4. **Google Container Registry** (gcr.io)
5. **Docker Hub Verified Publishers**
6. **Community registries** (case-by-case)

---

## 📝 Documentation Requirements

When adding an application from a source, document:

### In Chart README.md

```markdown
## Source

- **Operator/Chart Source:** [Link to operator or chart]
- **Image Registry:** [Quay.io, Docker Hub, etc.]
- **Image Repository:** [Full image path]
- **Upstream Project:** [Link to official project]
- **License:** [License type]

## Version Information

- **Chart Version:** 1.0.0
- **App Version:** 2.5.3
- **Last Updated:** 2025-11-07
```

### In Chart values.yaml

```yaml
# Image configuration
image:
  # Source: https://quay.io/repository/organization/image
  # Upstream: https://github.com/project/repo
  repository: quay.io/organization/image
  tag: "2.5.3"
  pullPolicy: IfNotPresent
```

### In PR Description

```markdown
## Application Source

- **Source Type:** Operator / Helm Chart / Custom Deployment
- **Source Link:** [URL]
- **Registry:** Quay.io / Docker Hub / ghcr.io
- **Image:** [Full image path with tag]
- **Official/Verified:** Yes / No
- **Security Scan:** Passed / Issues Found
- **OpenShift Compatible:** Yes / Needs adjustment

## Selection Rationale

- Why this source was chosen
- Alternatives considered
- Compatibility notes
```

---

## 🚀 Examples

### Example 1: Adding an Operator (Preferred)

```yaml
# Application: EMQX (MQTT Broker)
# Decision: Use official EMQX Operator

Source Evaluation:
1. ✅ Official EMQX Operator found on OperatorHub.io
2. ✅ Maturity: Seamless Upgrades
3. ✅ Helm chart available for operator deployment
4. ✅ OpenShift compatible
5. ✅ Recently updated (within 1 month)

Selected:
- Operator: EMQX Operator
- Source: https://artifacthub.io/packages/helm/emqx/emqx-operator
- Images: quay.io/emqx/emqx-operator
```

### Example 2: Adding a Helm Chart

```yaml
# Application: Plex Media Server
# Decision: Use community Helm chart (no operator available)

Source Evaluation:
1. ❌ No official operator found
2. ✅ Community Helm chart on ArtifactHub
3. ✅ Well-maintained (updated 2 weeks ago)
4. ⚠️ Needs OpenShift Route configuration
5. ✅ Security scan passed

Selected:
- Chart: Custom chart based on community example
- Base: https://artifacthub.io/packages/helm/k8s-at-home/plex
- Image: docker.io/linuxserver/plex (Verified Publisher)
```

### Example 3: Custom Deployment

```yaml
# Application: Glue Worker (Internal Tool)
# Decision: Custom Deployment (no existing chart/operator)

Source Evaluation:
1. ❌ No operator available (internal project)
2. ❌ No Helm chart available
3. ✅ Must build custom image and chart
4. ✅ Base image: python:3.12-slim (Official)

Selected:
- Custom Deployment: Built in-house
- Base Image: docker.io/library/python:3.12-slim
- Custom Image: Built from src/glue-worker/
```

---

## 🔗 Quick Links

- [ArtifactHub](https://artifacthub.io/)
- [OperatorHub.io](https://operatorhub.io/)
- [Quay.io](https://quay.io/)
- [Docker Hub](https://hub.docker.com/)
- [GitHub Container Registry](https://github.com/features/packages)
- [Google Container Registry](https://cloud.google.com/container-registry)

---

## 📚 Related Documentation

- [Adding an Application Checklist](../instructions/adding-an-application-checklist.md)
- [Chart Standards](../CHART-STANDARDS.md)
- [Security Best Practices](../reference/SECURITY-BEST-PRACTICES.md)
- [Documentation Index](../INDEX.md)

---

**Last Updated:** 2025-11-07
**Maintained By:** Repository maintainers
**See Also:** [Chart Standards](../CHART-STANDARDS.md), [Application Checklist](../instructions/adding-an-application-checklist.md)
