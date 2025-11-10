# Chart Standards Exceptions

This document tracks exceptions to the chart standards defined in [CHART-STANDARDS.md](./CHART-STANDARDS.md). Each exception includes the rationale and workaround implemented.

## Table of Contents

- [CyberChef - Nginx Cache Directories](#cyberchef---nginx-cache-directories)

---

## CyberChef - Nginx Cache Directories

**Chart:** `charts/applications/productivity/cyberchef`
**Date Added:** 2025-11-06
**Standard Violated:** Security - Uses anyuid SCC instead of restricted
**Issue:** Container image not designed for OpenShift restricted SCC

### Problem

The official CyberChef image (`ghcr.io/gchq/cyberchef`) runs nginx which requires:

1. Writable directories for cache and runtime files (`/var/cache/nginx`, `/var/run`)
2. Ability to bind to port 80 (requires root or CAP_NET_BIND_SERVICE)
3. Root user to modify nginx configuration at startup

When running as non-root user (OpenShift requirement), nginx fails with:

```text
nginx: [emerg] bind() to 0.0.0.0:80 failed (13: Permission denied)
```

### Root Cause

The upstream container image is built for traditional Docker environments, not Kubernetes/OpenShift security constraints. Nginx requires root privileges to bind to privileged ports (<1024) unless specifically compiled with capabilities support.

### Solution

Use OpenShift's `anyuid` SCC with RoleBinding to allow the ServiceAccount to run as any UID (including root):

```yaml
# ServiceAccount bound to anyuid SCC via RoleBinding
# Allows pod to run as root user for nginx port 80 binding
```

Added emptyDir volumes for writable directories:

```yaml
volumeMounts:
  - name: nginx-cache
    mountPath: /var/cache/nginx
  - name: nginx-run
    mountPath: /var/run

volumes:
  - name: nginx-cache
    emptyDir: {}
  - name: nginx-run
    emptyDir: {}
```

### Impact

- **Security:** ⚠️ Reduced - Pod runs as root (UID 0), but isolated to namespace
- **Functionality:** ✅ Application works correctly with upstream image
- **Performance:** ✅ No performance impact
- **Maintenance:** ✅ No divergence from upstream image

### Justification for anyuid SCC

CyberChef is:

- **Productivity tool** - Not exposed to internet, internal use only
- **Stateless** - No persistent data, runs entirely in-browser
- **Isolated** - NetworkPolicy restricts access to cluster users only
- **Low risk** - Even if compromised, limited blast radius (no PVCs, secrets, or external access)

### Alternative Considered

**Option 1:** Build custom nginx image on non-privileged port (8080)
**Rejected:** Requires maintaining custom Dockerfile, diverges from upstream, breaks on updates

**Option 2:** Use init container to rewrite nginx config
**Rejected:** Complex, fragile, breaks on image updates

**Option 3:** Find alternative CyberChef image
**Rejected:** No official OpenShift-compatible image exists

**Option 4:** Use nginx proxy with elevated privileges in separate pod
**Rejected:** Unnecessary architectural complexity for internal tool

### References

- OpenShift Documentation: [Managing Security Context Constraints](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)
- Kubernetes Documentation: [Volumes - emptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir)
- Chart Standards: [docs/CHART-STANDARDS.md](./CHART-STANDARDS.md)

---

## Template for New Exceptions

When adding a new exception, copy this template:

```markdown
## [Application Name] - [Brief Issue Description]

**Chart:** `charts/applications/<domain>/<app>`
**Date Added:** YYYY-MM-DD
**Standard Violated:** [Which standard from CHART-STANDARDS.md]
**Issue:** [Brief description]

### Problem

[Detailed description of the issue]

### Root Cause

[Why the standard can't be followed]

### Solution

[What workaround was implemented]

### Impact

- **Security:** [Security implications]
- **Functionality:** [Functional impact]
- **Performance:** [Performance considerations]
- **Maintenance:** [Maintenance burden]

### Alternative Considered

[Other options evaluated and why rejected]

### References

[Links to relevant documentation]
```

---

## Review Process

All exceptions should be:

1. **Documented** - Fully described in this file
2. **Justified** - Clear rationale for why standard cannot be met
3. **Reviewed** - Approved by maintainer
4. **Minimal** - Use least-privilege workaround possible
5. **Temporary** - Re-evaluated when upstream changes occur

## Periodic Review

Exceptions should be reviewed:

- **Quarterly** - Check if upstream has fixed the issue
- **On major version updates** - Test if exception is still needed
- **Before pattern releases** - Ensure all exceptions are still valid
