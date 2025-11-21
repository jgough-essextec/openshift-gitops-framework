# Example: Deploying MinIO ObjectStore

This guide shows how to deploy MinIO ObjectStore instances using the infrastructure ApplicationSet.

## Prerequisites

1. **AIStor MinIO Operator** must be installed first:
   ```yaml
   clusterGroup:
     platformComponents:
       aistorMinio:
         enabled: true
   ```

2. **Storage class** must be available (e.g., `truenas-iscsi`, `ocs-storagecluster-ceph-rbd`)

## Basic Deployment

### 1. Enable Infrastructure Applications
In your cluster values file:

```yaml
clusterGroup:
  applicationStacks:
    infrastructure:
      enabled: true
      apps:
        - minio-objectstore
```

### 2. Configure ObjectStore (Optional)
You can customize the ObjectStore by overriding values:

```yaml
# In your cluster values or separate values file
applications:
  minio-objectstore:
    objectstore:
      name: cluster-objectstore
      storage:
        storageClassName: "truenas-iscsi"
        volumeSize: "500Gi"
      
      pools:
        - name: pool-0
          servers: 4
          volumesPerServer: 4
      
      security:
        tls:
          enabled: true
        
    route:
      api:
        host: minio-api
      console:
        host: minio-console
```

## Deployment Examples

### Small Development Instance

```yaml
applications:
  minio-objectstore:
    objectstore:
      name: dev-minio
      storage:
        volumeSize: "50Gi"
      pools:
        - name: pool-0
          servers: 1
          volumesPerServer: 1
      resources:
        requests:
          memory: "512Mi"
          cpu: "250m"
        limits:
          memory: "1Gi"
          cpu: "500m"
```

### Production High-Availability Instance

```yaml
applications:
  minio-objectstore:
    objectstore:
      name: prod-minio
      storage:
        storageClassName: "fast-ssd"
        volumeSize: "1Ti"
      pools:
        - name: pool-0
          servers: 4
          volumesPerServer: 4
      resources:
        requests:
          memory: "2Gi"
          cpu: "1"
        limits:
          memory: "4Gi"
          cpu: "2"
      security:
        tls:
          enabled: true
          certSecret: "minio-production-tls"
      monitoring:
        enabled: true
```

### Multi-Pool Configuration

```yaml
applications:
  minio-objectstore:
    objectstore:
      name: multi-pool-minio
      storage:
        volumeSize: "500Gi"
      pools:
        - name: hot-storage
          servers: 4
          volumesPerServer: 2
        - name: warm-storage
          servers: 2
          volumesPerServer: 4
        - name: cold-storage
          servers: 1
          volumesPerServer: 8
```

## Access After Deployment

### Web Console
- URL: `https://minio-console.your-domain.com`
- Login with the generated credentials (check secret in namespace)

### S3 API Endpoint
- URL: `https://minio-api.your-domain.com`
- Use with any S3-compatible tool or SDK

### CLI Access
```bash
# Install mc (MinIO Client)
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configure alias
mc alias set mycluster https://minio-api.your-domain.com ACCESS_KEY SECRET_KEY

# Create bucket
mc mb mycluster/my-bucket

# Upload file
mc cp file.txt mycluster/my-bucket/
```

## Integration Examples

### Application Configuration
```yaml
env:
  - name: S3_ENDPOINT
    value: "https://minio-api.your-domain.com"
  - name: S3_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: cluster-objectstore-secret
        key: accesskey
  - name: S3_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: cluster-objectstore-secret
        key: secretkey
```

### Backup Target for Kasten K10
```yaml
# In Kasten policy
spec:
  actions:
  - action: backup
  - action: export
    exportParameters:
      frequency: "@daily"
      exportData:
        enabled: true
      location:
        type: objectStore
        objectStore:
          endpoint: "https://minio-api.your-domain.com"
          bucket: "k10-backups"
          prefix: "cluster-backups"
```

### Container Registry Backend
```yaml
# For OpenShift internal registry or external registry
spec:
  storage:
    s3:
      bucket: "registry-storage"
      region: "us-east-1"
      regionEndpoint: "https://minio-api.your-domain.com"
      secure: true
```

## Monitoring and Troubleshooting

### Check Deployment Status
```bash
# Check ApplicationSet
oc get applicationset -n openshift-gitops

# Check Application
oc get application minio-objectstore -n openshift-gitops

# Check ObjectStore
oc get objectstore -n aistor
oc describe objectstore cluster-objectstore -n aistor

# Check pods
oc get pods -n aistor -l app=minio

# Check services and routes
oc get svc,routes -n aistor
```

### Access Logs
```bash
# ObjectStore operator logs
oc logs -l app.kubernetes.io/name=object-store-operator -n aistor

# MinIO pods logs
oc logs -l app=minio -n aistor
```

### Common Issues

1. **Storage Class Not Found**: Ensure your storage class exists and is accessible
2. **Insufficient Resources**: Check cluster resource availability
3. **TLS Certificate Issues**: Verify certificate secrets exist
4. **Network Policies**: Ensure network policies allow traffic

## Performance Tuning

### Storage Performance
- Use fast storage classes (NVMe SSDs preferred)
- Configure appropriate `volumesPerServer` ratio
- Consider storage class parameters for performance

### Resource Allocation
- Increase memory for better caching
- Adjust CPU limits based on workload
- Monitor resource usage and adjust accordingly

### Network Configuration
- Use dedicated VLANs for storage traffic
- Consider network QoS settings
- Monitor network latency and throughput