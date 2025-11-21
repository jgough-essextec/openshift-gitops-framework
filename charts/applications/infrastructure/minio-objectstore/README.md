# MinIO ObjectStore Deployment

This Helm chart deploys MinIO ObjectStore instances using the AIStor MinIO Operator on OpenShift.

## Overview

This chart creates MinIO ObjectStore instances that provide high-performance, S3-compatible object storage for your applications. It's designed to work with the OpenShift GitOps framework and requires the AIStor MinIO Operator to be installed first.

## Prerequisites

- OpenShift 4.12+ cluster
- AIStor MinIO Operator installed (via the `aistor-minio-operator` platform component)
- Storage class available for persistent volumes
- Sufficient cluster resources

## Configuration

### Basic Configuration

```yaml
objectstore:
  enabled: true
  name: my-objectstore
  namespace: aistor
  
  storage:
    storageClassName: "truenas-iscsi"
    volumeSize: "100Gi"
  
  pools:
    - name: pool-0
      servers: 4
      volumesPerServer: 4
```

### Storage Configuration

The ObjectStore supports various storage configurations:

- **Storage Class**: Use your cluster's storage class (e.g., `truenas-iscsi`, `ocs-storagecluster-ceph-rbd`)
- **Volume Size**: Configure the size per volume
- **Pool Layout**: Configure servers and volumes per server for optimal performance

### Security Configuration

```yaml
objectstore:
  security:
    tls:
      enabled: true
      certSecret: "minio-tls-cert"  # Optional custom certificate
    rootUser: "admin"               # Optional: will auto-generate if not set
    rootPassword: "changeme123"     # Optional: will auto-generate if not set
```

### Access Configuration

```yaml
route:
  enabled: true
  api:
    host: minio-api
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  console:
    host: minio-console
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

This will create routes at:
- API: `https://minio-api.your-domain.com`
- Console: `https://minio-console.your-domain.com`

### Resource Configuration

```yaml
objectstore:
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1"
```

### Monitoring

```yaml
objectstore:
  monitoring:
    enabled: true
    path: "/minio/v2/metrics/cluster"
    port: 9000
    scrape: true
```

## Deployment Examples

### Small Development Instance

```yaml
objectstore:
  name: dev-objectstore
  pools:
    - name: pool-0
      servers: 1
      volumesPerServer: 1
  storage:
    volumeSize: "10Gi"
```

### Production High-Availability Instance

```yaml
objectstore:
  name: prod-objectstore
  pools:
    - name: pool-0
      servers: 4
      volumesPerServer: 4
  storage:
    volumeSize: "1Ti"
    storageClassName: "fast-ssd"
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"
```

### Multi-Pool Instance

```yaml
objectstore:
  name: multi-pool-objectstore
  pools:
    - name: hot-storage
      servers: 4
      volumesPerServer: 2
    - name: cold-storage
      servers: 2
      volumesPerServer: 4
  storage:
    volumeSize: "500Gi"
```

## Post-Deployment

After deployment, you can:

### Access the Console
Visit `https://minio-console.your-domain.com` to access the web console.

### Use the S3 API
The S3-compatible API is available at `https://minio-api.your-domain.com`.

### Configure Applications
Point your applications to the MinIO endpoint:

```yaml
env:
  - name: S3_ENDPOINT
    value: "https://minio-api.your-domain.com"
  - name: S3_BUCKET
    value: "my-bucket"
```

### Create Buckets
Use the console, CLI, or API to create buckets:

```bash
# Using mc client
mc alias set mycluster https://minio-api.your-domain.com ACCESS_KEY SECRET_KEY
mc mb mycluster/my-bucket
```

## Troubleshooting

### Check ObjectStore Status
```bash
oc get objectstore -n aistor
oc describe objectstore cluster-objectstore -n aistor
```

### Check Pods
```bash
oc get pods -n aistor -l app=minio
```

### Check Services
```bash
oc get services -n aistor
```

### Check Routes
```bash
oc get routes -n aistor
```

## Integration Examples

### Backup Storage for Kasten K10
```yaml
# Configure MinIO as backup location
spec:
  location:
    type: objectStore
    objectStore:
      endpoint: "https://minio-api.your-domain.com"
      bucket: "backup-storage"
```

### Container Registry Storage
```yaml
# Configure as backend for container registry
spec:
  storage:
    s3:
      bucket: "registry-storage"
      region: "us-east-1"
      regionEndpoint: "https://minio-api.your-domain.com"
```

## Links

- [MinIO Documentation](https://min.io/docs/)
- [AIStor MinIO Operator](https://github.com/minio/operator)
- [S3 API Reference](https://docs.aws.amazon.com/s3/)