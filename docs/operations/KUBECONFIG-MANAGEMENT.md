# Kubeconfig Management Guide

Best practices for managing multiple OpenShift cluster credentials and contexts.

**Last Updated:** 2025-11-07

---

## 📋 Overview

This guide covers strategies for managing kubeconfig files across multiple OpenShift clusters, including storage, security, context switching, and automation.

---

## 🎯 Storage Patterns

### Option 1: Single Kubeconfig with Multiple Contexts (Recommended)

**Description:** Merge all cluster configurations into one kubeconfig file with multiple contexts.

**Structure:**

```yaml
# ~/.kube/config
apiVersion: v1
kind: Config
current-context: sno
contexts:
  - name: sno
    context:
      cluster: sno-cluster
      user: admin-sno
  - name: hub
    context:
      cluster: hub-cluster
      user: admin-hub
  - name: test
    context:
      cluster: test-cluster
      user: admin-test
clusters:
  - name: sno-cluster
    cluster:
      server: https://api.sno.example.com:6443
      certificate-authority-data: <base64>
  - name: hub-cluster
    cluster:
      server: https://api.hub.example.com:6443
      certificate-authority-data: <base64>
users:
  - name: admin-sno
    user:
      token: <token>
```

**Pros:**

- ✅ Single file to manage
- ✅ Easy context switching
- ✅ Native `kubectl config use-context` support
- ✅ Works with kubectx/kubens tools

**Cons:**

- ❌ All credentials in one file (security concern)
- ❌ Can become large with many clusters
- ❌ Shared credentials across projects

**Usage:**

```bash
# Switch context
kubectl config use-context sno

# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts
```

---

### Option 2: Separate Files Per Cluster

**Description:** Maintain individual kubeconfig files for each cluster.

**Structure:**

```bash
~/.kube/
├── config-sno
├── config-hub
└── config-test
```

**Pros:**

- ✅ Isolated credentials per cluster
- ✅ Easy to share specific cluster access
- ✅ Better security boundaries
- ✅ Simpler to rotate individual credentials

**Cons:**

- ❌ Manual file switching required
- ❌ More files to manage
- ❌ Need helper scripts/functions

**Usage:**

```bash
# Set environment variable
export KUBECONFIG=~/.kube/config-sno

# Or use multiple files
export KUBECONFIG=~/.kube/config-sno:~/.kube/config-hub:~/.kube/config-test

# Switch via helper function
source ~/.kube/cluster-management.sh
use-cluster sno
```

---

### Option 3: Environment-Specific Directories

**Description:** Organize kubeconfigs by environment or project.

**Structure:**

```bash
~/.kube/
├── home/
│   ├── sno
│   └── hub
├── work/
│   ├── prod
│   └── test
└── lab/
    └── test
```

**Pros:**

- ✅ Clear separation by environment
- ✅ Easy to scope credentials
- ✅ Supports multiple projects
- ✅ Can apply different security policies per directory

**Cons:**

- ❌ More complex directory structure
- ❌ Requires path management
- ❌ Need automation for switching

---

## 🔒 Security Best Practices

### 1. Never Commit Kubeconfigs to Git

**Critical:** Kubeconfig files contain credentials and should NEVER be committed to version control.

**Ensure Git Ignore:**

```bash
# .gitignore
.kube/
*.kubeconfig
*kubeconfig*
config-*
```

**Check for Leaks:**

```bash
# Search for accidentally committed kubeconfigs
git log --all --full-history -- "*kubeconfig*"
git log --all --full-history -- "*.kube/*"
```

### 2. Use Short-Lived Tokens

**OpenShift Service Accounts:**

```bash
# Create service account with specific permissions
oc create serviceaccount automation -n default

# Grant permissions
oc adm policy add-cluster-role-to-user cluster-reader \
  system:serviceaccount:default:automation

# Get token (OpenShift 4.11+)
oc create token automation --duration=24h
```

**Temporary User Tokens:**

```bash
# Login and copy token
oc login --token=<token> --server=https://api.cluster.example.com:6443

# Token expires based on OAuth configuration
```

### 3. Encrypt at Rest

**Option A: Encrypted Filesystem**

```bash
# Use LUKS or similar for ~/.kube directory
# Or use encrypted home directory
```

**Option B: Secret Management Tools**

```bash
# Store in pass (password manager)
pass insert kube/sno-token
pass show kube/sno-token | oc login --token=-

# Store in 1Password CLI
op read "op://Kubernetes/sno/token" | oc login --token=-
```

### 4. Rotate Credentials Regularly

**Schedule:**

- **Production:** Every 90 days
- **Development:** Every 180 days
- **Personal Labs:** As needed

**Procedure:**

```bash
# 1. Generate new kubeconfig
oc login --server=<server> --username=<user>

# 2. Export to new file
oc config view --flatten > ~/.kube/config-sno-new

# 3. Test new config
KUBECONFIG=~/.kube/config-sno-new oc whoami

# 4. Replace old config
mv ~/.kube/config-sno ~/.kube/config-sno-backup
mv ~/.kube/config-sno-new ~/.kube/config-sno

# 5. Securely delete backup after verification
shred -u ~/.kube/config-sno-backup
```

### 5. Principle of Least Privilege

**Create role-based kubeconfigs:**

```bash
# View-only access
oc adm policy add-cluster-role-to-user view <user>

# Specific namespace access
oc adm policy add-role-to-user edit <user> -n <namespace>

# Project admin (not cluster admin)
oc adm policy add-role-to-user admin <user> -n <namespace>
```

---

## 🔄 Context Switching Methods

### Method 1: kubectl config (Native)

```bash
# List contexts
kubectl config get-contexts

# Switch context
kubectl config use-context sno

# View current context
kubectl config current-context

# Set namespace for context
kubectl config set-context --current --namespace=plex
```

### Method 2: KUBECONFIG Environment Variable

```bash
# Single cluster
export KUBECONFIG=~/.kube/config-sno

# Multiple clusters (merged)
export KUBECONFIG=~/.kube/config-sno:~/.kube/config-hub

# Temporary for single command
KUBECONFIG=~/.kube/config-test kubectl get nodes
```

### Method 3: kubectx/kubens (Recommended)

**Install:**

```bash
# macOS
brew install kubectx

# Linux
git clone https://github.com/ahmetb/kubectx ~/.kubectx
ln -s ~/.kubectx/kubectx /usr/local/bin/kubectx
ln -s ~/.kubectx/kubens /usr/local/bin/kubens
```

**Usage:**

```bash
# List contexts
kubectx

# Switch context
kubectx sno

# Previous context
kubectx -

# Switch namespace
kubens plex

# Previous namespace
kubens -
```

### Method 4: Custom Helper Functions

**Create cluster management functions:**

```bash
# ~/.kube/cluster-management.sh
export KUBECONFIG_DIR="$HOME/.kube"

# Helper to switch clusters
use-cluster() {
  local cluster=$1
  if [ -f "$KUBECONFIG_DIR/config-$cluster" ]; then
    export KUBECONFIG="$KUBECONFIG_DIR/config-$cluster"
    echo "✅ Switched to cluster: $cluster"
    oc whoami --show-server
  else
    echo "❌ Cluster config not found: $cluster"
    return 1
  fi
}

# Show current cluster
current-cluster() {
  if [ -z "$KUBECONFIG" ]; then
    echo "No KUBECONFIG set (using default)"
    kubectl config current-context 2>/dev/null || echo "No context"
  else
    echo "KUBECONFIG: $KUBECONFIG"
    kubectl config current-context 2>/dev/null || echo "No context"
  fi
  oc whoami --show-server 2>/dev/null || kubectl cluster-info 2>/dev/null
}

# List available clusters
list-clusters() {
  echo "Available cluster configs:"
  ls -1 "$KUBECONFIG_DIR"/config-* 2>/dev/null | sed 's/.*config-/  - /'
}

# Shorthand functions
alias sno='use-cluster sno'
alias hub='use-cluster hub'
alias test='use-cluster test'
alias current='current-cluster'
alias clusters='list-clusters'
```

**Add to shell profile:**

```bash
# ~/.bashrc or ~/.zshrc
source ~/.kube/cluster-management.sh
```

**Usage:**

```bash
# Switch to cluster
sno

# Check current cluster
current

# List available clusters
clusters
```

---

## 🚀 Multi-Cluster Workflows

### Workflow 1: Parallel Operations

**Run commands across multiple clusters:**

```bash
#!/bin/bash
# parallel-cluster-command.sh

CLUSTERS=("sno" "hub" "test")
COMMAND="$@"

for cluster in "${CLUSTERS[@]}"; do
  echo "=== $cluster ==="
  KUBECONFIG=~/.kube/config-$cluster bash -c "$COMMAND"
  echo
done
```

**Usage:**

```bash
./parallel-cluster-command.sh "oc get nodes"
./parallel-cluster-command.sh "oc get applications -n openshift-gitops"
```

### Workflow 2: Cluster Comparison

**Compare resources across clusters:**

```bash
#!/bin/bash
# compare-clusters.sh

RESOURCE=$1
NAMESPACE=${2:-default}

echo "Comparing $RESOURCE in namespace $NAMESPACE"
echo

for cluster in sno hub test; do
  echo "=== $cluster ==="
  KUBECONFIG=~/.kube/config-$cluster \
    kubectl get $RESOURCE -n $NAMESPACE -o wide
  echo
done
```

**Usage:**

```bash
./compare-clusters.sh pods openshift-gitops
./compare-clusters.sh applications openshift-gitops
```

### Workflow 3: Sequential Deployment

**Deploy to clusters in sequence (dev → test → prod):**

```bash
#!/bin/bash
# sequential-deploy.sh

CLUSTERS=("test" "hub" "sno")  # test -> hub -> prod (sno)

for cluster in "${CLUSTERS[@]}"; do
  echo "=== Deploying to $cluster ==="

  # Switch cluster
  export KUBECONFIG=~/.kube/config-$cluster

  # Sync all applications
  oc get applications -n openshift-gitops -o name | \
    xargs -I {} argocd app sync {}

  # Wait for sync
  echo "Waiting for sync to complete..."
  sleep 30

  # Check health
  oc get applications -n openshift-gitops

  # Prompt to continue
  read -p "Continue to next cluster? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
done

echo "✅ Deployment complete across all clusters"
```

### Workflow 4: Health Check Dashboard

**Quick health check across clusters:**

```bash
#!/bin/bash
# cluster-health-dashboard.sh

check_cluster() {
  local cluster=$1
  local kubeconfig=~/.kube/config-$cluster

  if [ ! -f "$kubeconfig" ]; then
    echo "  Status: ❌ Config not found"
    return
  fi

  # Check connectivity
  if ! KUBECONFIG=$kubeconfig oc whoami --show-server &>/dev/null; then
    echo "  Status: ❌ Not reachable"
    return
  fi

  # Get node count
  local nodes=$(KUBECONFIG=$kubeconfig oc get nodes --no-headers 2>/dev/null | wc -l)

  # Get application count
  local apps=$(KUBECONFIG=$kubeconfig oc get applications -n openshift-gitops --no-headers 2>/dev/null | wc -l)

  # Get unhealthy applications
  local unhealthy=$(KUBECONFIG=$kubeconfig oc get applications -n openshift-gitops -o json 2>/dev/null | \
    jq -r '.items[] | select(.status.health.status != "Healthy") | .metadata.name' | wc -l)

  echo "  Status: ✅ Online"
  echo "  Nodes: $nodes"
  echo "  Applications: $apps"
  if [ "$unhealthy" -gt 0 ]; then
    echo "  ⚠️  Unhealthy Apps: $unhealthy"
  else
    echo "  Unhealthy Apps: 0"
  fi
}

echo "=== Cluster Health Dashboard ==="
echo

for cluster in sno hub test; do
  echo "$cluster:"
  check_cluster $cluster
  echo
done
```

---

## 🔧 Devcontainer Integration

### Argo-Apps Devcontainer Setup

This repository includes devcontainer cluster management functions.

**Location:** `.devcontainer/cluster-management.sh`

**Available Functions:**

```bash
# Switch clusters
sno         # Switch to SNO cluster
hub         # Switch to hub cluster
test        # Switch to test cluster

# Check status
current-cluster     # Show current cluster and connection info
cluster-status      # Check status of all configured clusters

# List clusters
clusters    # List available kubeconfig files
```

**Configuration:**

Kubeconfig files should be placed in `/workspaces/argo-apps/.kube/`:

```
/workspaces/argo-apps/
└── .kube/
    ├── config-sno
    ├── config-hub
    └── config-test
```

**Automatic Loading:**

The devcontainer automatically sources cluster management functions on startup.

### VS Code Kubernetes Extension

**Install:** [Kubernetes Extension](https://marketplace.visualstudio.com/items?itemName=ms-kubernetes-tools.vscode-kubernetes-tools)

**Features:**

- Visual cluster switching
- Resource browsing
- Pod logs and shells
- Apply/delete resources
- Port forwarding

**Configuration:**

```json
// .vscode/settings.json
{
  "vs-kubernetes": {
    "vs-kubernetes.kubeconfig": "${env:KUBECONFIG}",
    "vs-kubernetes.kubectl-path": "/usr/local/bin/kubectl",
    "vs-kubernetes.namespace": "default"
  }
}
```

---

## 📊 Cluster Inventory Management

### Cluster Metadata File

**Create cluster inventory:**

```yaml
# ~/.kube/clusters.yaml
clusters:
  sno:
    name: Single Node OpenShift
    environment: production
    api: https://api.sno.example.com:6443
    kubeconfig: ~/.kube/config-sno
    topology: sno
    location: Home Lab
    contact: admin@example.com

  hub:
    name: Hub Cluster
    environment: production
    api: https://api.hub.example.com:6443
    kubeconfig: ~/.kube/config-hub
    topology: full
    location: Home Lab
    contact: admin@example.com

  test:
    name: Test Cluster
    environment: test
    api: https://api.test.example.com:6443
    kubeconfig: ~/.kube/config-test
    topology: compact
    location: Home Lab
    contact: admin@example.com
```

### Inventory Query Script

```bash
#!/bin/bash
# query-clusters.sh

INVENTORY=~/.kube/clusters.yaml

# Requires yq (https://github.com/mikefarah/yq)

list_clusters() {
  yq eval '.clusters | keys | .[]' $INVENTORY
}

get_cluster_info() {
  local cluster=$1
  yq eval ".clusters.$cluster" $INVENTORY
}

get_cluster_api() {
  local cluster=$1
  yq eval ".clusters.$cluster.api" $INVENTORY
}

# List all production clusters
list_production_clusters() {
  yq eval '.clusters | to_entries | .[] | select(.value.environment == "production") | .key' $INVENTORY
}

# Usage examples
case "$1" in
  list)
    list_clusters
    ;;
  info)
    get_cluster_info "$2"
    ;;
  api)
    get_cluster_api "$2"
    ;;
  prod)
    list_production_clusters
    ;;
  *)
    echo "Usage: $0 {list|info <cluster>|api <cluster>|prod}"
    ;;
esac
```

---

## 🎯 Best Practices Summary

### Do's ✅

- ✅ Use separate kubeconfig files per cluster for better security
- ✅ Always verify current cluster before running commands
- ✅ Use helper functions or kubectx for easy switching
- ✅ Keep kubeconfigs in `~/.kube/` or secure location
- ✅ Add kubeconfig patterns to `.gitignore`
- ✅ Rotate credentials regularly
- ✅ Use short-lived tokens when possible
- ✅ Document cluster inventory with metadata
- ✅ Test commands on non-prod clusters first
- ✅ Encrypt kubeconfigs at rest

### Don'ts ❌

- ❌ Never commit kubeconfigs to Git
- ❌ Never share kubeconfig files directly
- ❌ Never use cluster-admin for routine operations
- ❌ Never skip context verification before destructive operations
- ❌ Never store kubeconfigs in unencrypted cloud storage
- ❌ Never use the same credentials across environments
- ❌ Never keep expired or unused kubeconfigs
- ❌ Never run untested commands on production
- ❌ Never bypass RBAC with service account tokens

---

## 🐛 Troubleshooting

### Issue: "Error: unknown flag: --show-server"

**Cause:** Using kubectl instead of oc

**Solution:**

```bash
# OpenShift
oc whoami --show-server

# Kubernetes
kubectl cluster-info | head -1
```

### Issue: "The connection to the server was refused"

**Cause:** Cluster unreachable or wrong context

**Solution:**

```bash
# Check current context
current-cluster

# Check cluster connectivity
oc whoami --show-server

# Verify kubeconfig
cat $KUBECONFIG | grep server:

# Test connectivity
curl -k $(oc whoami --show-server)/healthz
```

### Issue: "Forbidden: User cannot list resources"

**Cause:** Insufficient permissions

**Solution:**

```bash
# Check current user/service account
oc whoami

# Check permissions
oc auth can-i get pods
oc auth can-i list projects

# Request additional permissions from cluster admin
```

### Issue: Commands execute on wrong cluster

**Cause:** Forgot to switch context

**Solution:**

```bash
# Always verify before commands
current-cluster

# Use explicit KUBECONFIG
KUBECONFIG=~/.kube/config-test oc get pods

# Create shell aliases with built-in verification
alias oc-sno='current-cluster && oc'
```

---

## 📚 Related Documentation

- [Multi-Cluster Management](./MULTI-CLUSTER-MANAGEMENT.md)
- [Security Best Practices](../reference/SECURITY-BEST-PRACTICES.md)
- [Devcontainer Documentation](../../.devcontainer/README.md)
- [Documentation Index](../INDEX.md)

---

## 🔗 External Resources

- [kubectl Config Documentation](https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/)
- [kubectx/kubens](https://github.com/ahmetb/kubectx)
- [OpenShift CLI Documentation](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html)

---

**Last Updated:** 2025-11-07
**Maintained By:** Repository maintainers
**See Also:** [Known Gaps - Kubeconfig Management](../KNOWN-GAPS.md#kubeconfig-management)
