# Application Sources - Quick Reference

One-page reference for finding applications, operators, and images.

**Last Updated:** 2025-11-07

---

## 🔍 Search Priority

### 1️⃣ Check for Operator (FIRST!)

**Search:** [OperatorHub.io](https://operatorhub.io/)

```bash
# Search URL pattern
https://operatorhub.io/?keyword=<app-name>
```

**Priority:**

1. 🏆 Red Hat Certified Operators (production-ready, supported)
2. 🥇 Certified Partners (verified partners)
3. 🥈 Community Operators (community-maintained)

**What to check:**

- Operator maturity level (Seamless Upgrades > Full Lifecycle > Basic Install)
- OpenShift support
- Documentation quality
- Recent updates

---

### 2️⃣ Check for Helm Chart

**Search:** [ArtifactHub.io](https://artifacthub.io/)

```bash
# Search URL pattern
https://artifacthub.io/packages/search?ts_query_web=<app-name>&sort=relevance
```

**Priority:**

1. 🏆 Official repository (by project maintainers)
2. 🥇 Verified publisher
3. 🥈 CNCF projects
4. 🥉 Community charts (well-maintained)

**Filters to apply:**

- Official repository: ✅
- Verified publisher: ✅
- Updated < 3 months: ✅
- Security scan passed: ✅
- Has documentation: ✅

---

### 3️⃣ Find Container Image

**Registries (in order):**

#### A. Quay.io (Red Hat/OpenShift)

```bash
https://quay.io/search?q=<app-name>
```

**Preferred namespaces:**

- `redhat/` - Red Hat official
- `openshift/` - OpenShift components
- `<project>/` - Official project images

#### B. Docker Hub (General)

```bash
https://hub.docker.com/search?q=<app-name>
```

**Look for:**

- Official Image badge (⭐)
- Verified Publisher (✓)
- High pull count
- Recent updates

#### C. GitHub Container Registry

```bash
https://github.com/<org>/<repo>/pkgs/container/<image>
# or
ghcr.io/<org>/<image>
```

---

## ✅ Quick Evaluation Checklist

Before adding any application:

### Security

- [ ] Official or verified source
- [ ] Security scanning enabled and passed
- [ ] No critical CVEs
- [ ] Runs as non-root
- [ ] Restricted SCC compatible

### Quality

- [ ] Recently updated (< 3 months ideal)
- [ ] Good documentation
- [ ] Active maintainers
- [ ] OpenShift compatible

### License

- [ ] Open source license
- [ ] No proprietary restrictions
- [ ] Organization policy compliant

---

## 🎯 Decision Flow

```
NEW APPLICATION NEEDED
        ↓
  Operator exists? ──YES──> Use Operator (OperatorHub/ArtifactHub)
        ↓ NO                      ↓
                           Deploy to charts/platform/ or
                           charts/applications/infrastructure/
        ↓
  Helm chart exists? ──YES──> Use Chart (ArtifactHub)
        ↓ NO                      ↓
                           Deploy to charts/applications/<domain>/
        ↓
  Build custom chart
  with official image
        ↓
  Find official image:
  1. Quay.io
  2. Docker Hub
  3. ghcr.io
        ↓
  Deploy to charts/applications/<domain>/
```

---

## 📋 Complete Workflow

```bash
# 1. Search for operator
open https://operatorhub.io/?keyword=<app-name>

# 2. If no operator, search for Helm chart
open https://artifacthub.io/packages/search?ts_query_web=<app-name>

# 3. If no chart, find official image
open https://quay.io/search?q=<app-name>
open https://hub.docker.com/search?q=<app-name>

# 4. Create chart using scaffolding tool
./scripts/chart-tools/scaffold-new-chart.sh <domain> <app-name>

# 5. Follow checklist
# See: docs/instructions/adding-an-application-checklist.md
```

---

## 🔗 External Links

### Search Engines

- [OperatorHub.io](https://operatorhub.io/) - Kubernetes operators
- [ArtifactHub.io](https://artifacthub.io/) - Helm charts, operators, OLM
- [Quay.io](https://quay.io/) - Container registry (Red Hat)
- [Docker Hub](https://hub.docker.com/) - Container registry (Docker)
- [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) - GitHub Container Registry

### Documentation

- [CNCF Projects](https://www.cncf.io/projects/) - Cloud Native projects
- [OpenShift Operators](https://docs.openshift.com/container-platform/latest/operators/index.html)
- [Operator Maturity Model](https://operatorframework.io/operator-capabilities/)

---

## 💡 Tips

### Finding Official Sources

- Check project's official website/docs
- Look for "Kubernetes deployment" or "Operator" sections
- Check project's GitHub releases
- Search project's container registry

### Red Flags (Avoid)

- ❌ No updates in > 6 months
- ❌ No documentation
- ❌ Critical CVEs unfixed
- ❌ Unknown/untrusted publisher
- ❌ No license or proprietary
- ❌ Requires cluster-admin

### Green Flags (Prefer)

- ✅ Official/verified publisher
- ✅ Regular updates
- ✅ Good documentation
- ✅ Active community
- ✅ Security scanning
- ✅ OpenShift tested
- ✅ Namespace-scoped

---

## 📚 Related Documentation

- [Detailed Guide](./PREFERRED-SOURCES.md) - Complete documentation
- [Adding Application Checklist](../instructions/adding-an-application-checklist.md)
- [Chart Standards](../CHART-STANDARDS.md)
- [Documentation Index](../INDEX.md)

---

**Print this page:** Use your browser's print function or save as PDF for quick reference.

**Bookmark these searches:**

- [OperatorHub Search](https://operatorhub.io/)
- [ArtifactHub Search](https://artifacthub.io/packages/search)
- [Quay Search](https://quay.io/search)
- [Docker Hub Search](https://hub.docker.com/search)
