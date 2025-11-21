# AIStor MinIO Operator

This Helm chart deploys the AIStor MinIO Operator on OpenShift, providing S3-compatible object storage capabilities.

## Overview

The AIStor MinIO Operator enables deployment and management of MinIO instances in your OpenShift cluster. MinIO provides high-performance, S3-compatible object storage that's ideal for:

- Application data storage
- Backup and archival
- Data lakes and analytics
- Container image registry storage
- Static website hosting

## Components

This chart deploys:
- **Subscription**: Installs the AIStor MinIO Operator from OperatorHub
- **Namespace**: Creates a dedicated namespace for the operator
- **OperatorConfig**: Configures the operator with sensible defaults

## Configuration

### Basic Configuration

```yaml
namespace:
  create: true
  name: aistor-minio-system

subscription:
  channel: stable
  installPlanApproval: Automatic
```

### Operator Configuration

```yaml
operatorconfig:
  enabled: true
```

## Post-Installation

After the operator is installed, you can create MinIO instances using the `MinIOCluster` custom resource:

```yaml
apiVersion: minio.aistor.io/v1
kind: MinIOCluster
metadata:
  name: my-minio-cluster
  namespace: my-namespace
spec:
  replicas: 4
  volumeClaimTemplate:
    spec:
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 10Gi
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
```

## Links

- [MinIO Documentation](https://min.io/docs/)
- [AIStor MinIO Operator](https://github.com/aistor/minio-operator)
- [S3 API Reference](https://docs.aws.amazon.com/s3/)