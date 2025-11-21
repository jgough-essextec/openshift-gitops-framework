# Example: How to enable AIStor MinIO Operator

To enable the AIStor MinIO operator in your cluster, add the following to your cluster-specific values file:

## In your cluster values file (e.g., clusters/individual-clusters/values-mycluster.yaml):

```yaml
clusterGroup:
  platformComponents:
    aistorMinio:
      enabled: true
```

## Creating a MinIO Instance

After the operator is installed, you can create MinIO instances using the `MinIOCluster` custom resource:

```yaml
apiVersion: minio.aistor.io/v1
kind: MinIOCluster
metadata:
  name: production-minio
  namespace: minio-production
spec:
  replicas: 4
  image: "quay.io/minio/minio:RELEASE.2024-01-16T16-07-38Z"
  
  # Storage configuration
  volumeClaimTemplate:
    spec:
      accessModes:
        - ReadWriteOnce
      storageClassName: truenas-iscsi  # Or your preferred storage class
      resources:
        requests:
          storage: 100Gi
  
  # Security configuration
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  
  # Service configuration
  service:
    type: ClusterIP
    port: 9000
    consolePort: 9001
  
  # TLS configuration (optional)
  tls:
    enabled: true
    certSecret: minio-tls-cert
  
  # Environment variables
  env:
    - name: MINIO_PROMETHEUS_AUTH_TYPE
      value: "public"
```

## Accessing MinIO

After deployment, you can access MinIO through:

1. **Console UI**: `http(s)://minio-console.<your-domain>`
2. **S3 API**: `http(s)://minio-api.<your-domain>`
3. **mc client**: 
   ```bash
   mc alias set mycluster http://minio-api.example.com ACCESS_KEY SECRET_KEY
   ```

## Integration Examples

### With applications requiring S3 storage:
```yaml
env:
  - name: S3_ENDPOINT
    value: "minio-api.minio-production.svc.cluster.local:9000"
  - name: S3_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: minio-credentials
        key: accesskey
  - name: S3_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: minio-credentials
        key: secretkey
```

### With Backup tools (like Kasten K10):
```yaml
# Configure MinIO as backup target
location:
  type: objectStore
  objectStore:
    endpoint: "http://minio-api.minio-production.svc.cluster.local:9000"
    bucket: "backup-storage"
    prefix: "k10-backups"
```