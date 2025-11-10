---
applyTo: "charts/ai/**"
---

# AI Domain - Application Guidelines

This document provides domain-specific guidelines for AI and Machine Learning applications in the `charts/ai/` directory.

## Domain Overview

**Purpose:** AI/ML applications, inference engines, training platforms, and supporting services

**ApplicationSet:** `roles/<cluster>/templates/ai.yaml`

**Common Characteristics:**

- GPU requirements (AMD/Intel/NVIDIA)
- High memory/CPU usage
- Model storage needs
- API-based services
- Web interfaces for interaction

## Domain-Specific Requirements

### GPU Support

AI applications often require GPU acceleration:

```yaml
# values.yaml
resources:
  limits:
    amd.com/gpu: 1 # For AMD GPUs
    # OR
    gpu.intel.com/i915: 1 # For Intel GPUs

nodeSelector:
  feature.node.kubernetes.io/pci-10de.present: "true" # NVIDIA
  # OR
  feature.node.kubernetes.io/pci-1002.present: "true" # AMD
  # OR
  feature.node.kubernetes.io/pci-8086.present: "true" # Intel
```

**Checklist:**

- [ ] GPU requirements documented in README.md
- [ ] GPU limits configurable via values.yaml
- [ ] Node selectors based on NFD labels
- [ ] Fallback to CPU-only mode (if applicable)

### Model Storage

AI apps need persistent storage for models:

```yaml
# values.yaml
persistence:
  models:
    enabled: true
    storageClass: truenas-iscsi-csi # or appropriate storage class
    size: 50Gi # Adjust based on model sizes
    mountPath: /models
```

**Checklist:**

- [ ] Model storage persistent (not ephemeral)
- [ ] Storage size appropriate for models (LLMs: 10-100GB+)
- [ ] Mount path consistent with application expectations
- [ ] Consider using TrueNAS for home clusters

### Memory Requirements

AI applications are memory-intensive:

```yaml
# values.yaml
resources:
  requests:
    memory: 4Gi # Minimum for small models
    cpu: 2000m
  limits:
    memory: 16Gi # Allow burst for inference
```

**Checklist:**

- [ ] Memory requests reflect actual usage (check with VPA/Goldilocks)
- [ ] Memory limits set high enough to prevent OOMKills
- [ ] CPU requests appropriate for inference workload
- [ ] Consider StatefulSet for stateful applications

### API Endpoints

Most AI applications expose APIs:

```yaml
# values.yaml
service:
  type: ClusterIP
  port: 8000 # Common for AI APIs
  targetPort: 8000

route:
  enabled: true
  tls:
    termination: edge # Or reencrypt if app has TLS
```

**Checklist:**

- [ ] API endpoint documented in README
- [ ] OpenAPI/Swagger docs linked (if available)
- [ ] Authentication mechanism documented
- [ ] Rate limiting considered

### Health Checks

AI applications may have slow startup (model loading):

```yaml
# templates/deployment.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 60 # Allow time for model loading
  periodSeconds: 30
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Checklist:**

- [ ] Initial delay sufficient for model loading
- [ ] Health endpoint responds quickly
- [ ] Readiness separate from liveness
- [ ] Startup probe for very slow starts (optional)

## Common AI Application Patterns

### Inference Engines (Ollama, LiteLLM)

**Characteristics:**

- Model serving
- API endpoints
- GPU acceleration
- Large model storage

**Template Reference:** `charts/ai/ollama/` or `charts/ai/litellm/`

### Web UIs (Open WebUI, Jupyter)

**Characteristics:**

- Web interface
- User authentication
- Session persistence
- API integration

**Template Reference:** `charts/ai/open-webui/`

### Training Platforms

**Characteristics:**

- Job-based workloads
- Distributed training
- Dataset storage
- GPU scheduling

**Coming Soon**

## Integration Patterns

### External Secrets

AI apps often need API keys:

```yaml
# templates/externalsecret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ include "app.fullname" . }}
spec:
  secretStoreRef:
    name: infisical-secret-store
    kind: ClusterSecretStore
  target:
    name: {{ include "app.fullname" . }}-secrets
  data:
    - secretKey: OPENAI_API_KEY
      remoteRef:
        key: openai-api-key
```

**Checklist:**

- [ ] API keys from External Secrets (not hard-coded)
- [ ] Secret store configured (Infisical for home clusters)
- [ ] Secrets documented in chart README

### Model Caching

Share models between applications:

```yaml
# values.yaml
persistence:
  modelCache:
    enabled: true
    existingClaim: ai-models-shared # Shared PVC
    mountPath: /models
```

**Checklist:**

- [ ] Consider shared PVC for common models
- [ ] Document model cache location
- [ ] Handle concurrent access safely

### Monitoring (Gatus)

```yaml
# values.yaml
gatus:
  enabled: true
  interval: 5m
  conditions:
    - "[STATUS] == 200"
    - "[RESPONSE_TIME] < 5000" # AI inference can be slow
```

**Checklist:**

- [ ] Gatus monitoring enabled by default
- [ ] Response time threshold realistic for AI workloads
- [ ] Health endpoint tested

## Security Considerations

### API Access

AI APIs should be protected:

- [ ] OpenShift Route with TLS
- [ ] Authentication required (OAuth, API keys, etc.)
- [ ] Network policies to restrict access (optional)
- [ ] Rate limiting at Route level (if needed)

### Model Security

- [ ] Models stored on encrypted storage
- [ ] Access controls on model storage
- [ ] Model provenance documented

### Data Privacy

- [ ] No PII in logs
- [ ] Data retention policies documented
- [ ] Compliance requirements noted in README

## Performance Optimization

### Resource Tuning

After deployment, use VPA/Goldilocks:

```bash
# Check VPA recommendations
oc get vpa -n <app-name>

# View in Goldilocks dashboard
https://goldilocks.apps.<cluster>.<domain>
```

**Checklist:**

- [ ] Initial resource requests conservative
- [ ] Monitor with Goldilocks after 24-48 hours
- [ ] Adjust based on actual usage
- [ ] Document final resource requirements

### GPU Scheduling

- [ ] GPU time-slicing configured (if needed)
- [ ] GPU quotas set per namespace (if multi-tenant)
- [ ] GPU metrics monitored

## Examples from Existing Charts

### LiteLLM (API Gateway)

- Path: `charts/ai/litellm/`
- Pattern: API gateway for multiple LLM providers
- Features: Route, Service, Deployment, External Secrets, Gatus

### Ollama (Model Server)

- Path: `charts/ai/ollama/`
- Pattern: Local LLM inference engine
- Features: GPU support, Model storage, API endpoint

### Open WebUI (Web Interface)

- Path: `charts/ai/open-webui/`
- Pattern: Chat interface for AI models
- Features: Web UI, Authentication, API integration

## Testing Checklist

Before deploying AI applications:

- [ ] Test without GPU first (if CPU fallback exists)
- [ ] Test with GPU on appropriate nodes
- [ ] Verify model loading completes successfully
- [ ] Test API endpoints respond correctly
- [ ] Check memory usage doesn't cause OOMKills
- [ ] Verify persistent storage works across pod restarts
- [ ] Test Route/Ingress accessibility
- [ ] Verify External Secrets populate correctly

## Troubleshooting

### GPU Not Detected

```bash
# Check NFD labels
oc get node <node-name> -o yaml | grep feature.node.kubernetes.io/pci

# Check GPU operator
oc get pods -n amd-gpu-operator  # or nvidia-gpu-operator

# Check device plugin
oc get daemonset -n kube-system | grep gpu
```

### Model Loading Failures

```bash
# Check persistent volume
oc get pvc -n <app-name>
oc describe pvc <pvc-name> -n <app-name>

# Check pod logs
oc logs -n <app-name> <pod-name> --tail=100

# Check storage class
oc get storageclass
```

### High Memory Usage

```bash
# Check current usage
oc top pod -n <app-name>

# Check for OOMKills
oc get events -n <app-name> | grep OOM

# Increase limits
# Edit values.yaml: resources.limits.memory
```

### Slow API Responses

```bash
# Check if GPU is being used
oc exec -n <app-name> <pod-name> -- nvidia-smi  # NVIDIA
oc exec -n <app-name> <pod-name> -- rocm-smi    # AMD

# Check CPU/memory throttling
oc describe pod -n <app-name> <pod-name> | grep -A 5 "Limits\|Requests"

# Check network latency
oc exec -n <app-name> <pod-name> -- ping -c 5 <external-api>
```

## References

- [AI Stack Documentation](../../docs/ai-stack/)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [AMD GPU Operator](https://github.com/ROCm/k8s-device-plugin)
- [Intel GPU Device Plugin](https://github.com/intel/intel-device-plugins-for-kubernetes)
- [Model Optimization Techniques](https://huggingface.co/docs/transformers/perf_train_gpu_one)

## Questions?

If you have questions about AI domain patterns, check:

1. Existing AI charts in `charts/ai/`
2. AI stack documentation in `docs/ai-stack/`
3. Chart standards in `docs/CHART-STANDARDS.md`
