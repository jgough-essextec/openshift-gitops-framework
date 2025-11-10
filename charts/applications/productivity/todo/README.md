# Todo Application Helm Chart

Petri Dish Todo Application - A modern task management application with hierarchical todos, featuring a FastAPI backend and React frontend.

## Description

This Helm chart deploys the Petri Dish Todo application on OpenShift, providing a full-stack solution for hierarchical task management. The application consists of:

- **Backend**: FastAPI (Python) REST API with SQLite database
- **Frontend**: React application with Bootstrap UI

## Features

- Hierarchical todo structure (parent-child relationships)
- Pagination support for large todo lists
- Search functionality
- Filter by completed/active status
- Todo history view
- RESTful API with FastAPI
- Persistent SQLite database storage
- OpenShift Route for external access
- Gatus monitoring integration

## Prerequisites

- OpenShift 4.x or Kubernetes 1.19+
- Helm 3.x
- Persistent storage (for backend database)
- Container images built and pushed to registry:
  - Backend: `quay.io/rbales79/todo-backend:latest`
  - Frontend: `quay.io/rbales79/todo-frontend:latest`

## Building Container Images

Before deploying, build and push the container images:

```bash
# Clone the source repository
git clone https://github.com/jgough-essextec/the_petri_dish.git
cd the_petri_dish
git checkout open-shift-build

# Build backend image
podman build -t quay.io/rbales79/todo-backend:latest -f backend/Dockerfile .
podman push quay.io/rbales79/todo-backend:latest

# Build frontend image
podman build -t quay.io/rbales79/todo-frontend:latest -f frontend/Dockerfile .
podman push quay.io/rbales79/todo-frontend:latest
```

## Installation

### Via ArgoCD (GitOps)

1. Add the application to your cluster's values file (`values-<cluster>.yaml`):

```yaml
clusterGroup:
  applicationStacks:
    productivity:
      enabled: true
      apps:
        - todo
```

2. The ApplicationSet will automatically deploy the application.

### Via Helm CLI

```bash
# Install in the todo namespace
helm install todo ./charts/applications/productivity/todo \
  --namespace todo \
  --create-namespace \
  --set cluster.name=<cluster-name> \
  --set cluster.top_level_domain=<domain>
```

## Configuration

### Key Values

| Parameter                     | Description                | Default                          |
| ----------------------------- | -------------------------- | -------------------------------- |
| `backend.enabled`             | Enable backend deployment  | `true`                           |
| `backend.image.repository`    | Backend image repository   | `quay.io/rbales79/todo-backend`  |
| `backend.image.tag`           | Backend image tag          | `latest`                         |
| `backend.persistence.enabled` | Enable persistent storage  | `true`                           |
| `backend.persistence.size`    | PVC size for database      | `5Gi`                            |
| `frontend.enabled`            | Enable frontend deployment | `true`                           |
| `frontend.image.repository`   | Frontend image repository  | `quay.io/rbales79/todo-frontend` |
| `frontend.image.tag`          | Frontend image tag         | `latest`                         |
| `route.enabled`               | Create OpenShift Route     | `true`                           |
| `route.tls.enabled`           | Enable TLS on Route        | `true`                           |
| `gatus.enabled`               | Enable Gatus monitoring    | `true`                           |

### Example Custom Values

```yaml
backend:
  replicaCount: 2
  persistence:
    size: 10Gi
    storageClass: "truenas-iscsi-csi"
  resources:
    requests:
      cpu: 200m
      memory: 256Mi

frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi

route:
  host: "todo.example.com"
```

## OpenShift Integration

### Route

The chart creates an OpenShift Route for external access:

- **URL**: `https://todo.apps.<cluster>.<domain>`
- **TLS**: Edge termination (default)
- **Backend**: Frontend service (React app)

### Security

The chart is designed to work with OpenShift's restricted SCC:

- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- Capabilities dropped: `ALL`
- `seccompProfile: RuntimeDefault`

### Service Account

A dedicated ServiceAccount is created for the application with minimal permissions.

## API Endpoints

The backend provides the following REST API endpoints:

| Method | Endpoint               | Description                           |
| ------ | ---------------------- | ------------------------------------- |
| GET    | `/todos/`              | List all active todos with pagination |
| POST   | `/todos/`              | Create a new todo                     |
| GET    | `/todos/{id}`          | Get a specific todo                   |
| PUT    | `/todos/{id}`          | Update a todo                         |
| DELETE | `/todos/{id}`          | Delete a todo                         |
| GET    | `/todos/completed/`    | List completed todos                  |
| PUT    | `/todos/{id}/complete` | Mark todo as complete                 |
| GET    | `/todos/search/`       | Search todos by text                  |
| GET    | `/todos/hierarchy/`    | Get hierarchical todo structure       |

API documentation is available at `/docs` (FastAPI Swagger UI).

## Monitoring

### Gatus Integration

When `gatus.enabled: true`, the chart creates a ConfigMap for Gatus monitoring:

- **Frontend endpoint**: Monitors the web UI
- **Backend endpoint**: Monitors the API health
- **Alerts**: Slack notifications on failures

## Persistence

The backend requires persistent storage for the SQLite database:

- **Default size**: 5Gi
- **Access mode**: ReadWriteOnce
- **Mount path**: `/app/data`
- **Database file**: `/app/data/todos.db`

## Troubleshooting

### Backend Database Issues

Check backend logs:

```bash
oc logs -n todo deployment/todo-backend -f
```

Verify PVC is bound:

```bash
oc get pvc -n todo
```

### Frontend Not Connecting to Backend

The frontend uses `/api` as a proxy to the backend. Verify:

1. Backend service is running:

   ```bash
   oc get svc -n todo
   ```

2. Frontend environment variable is set correctly:
   ```bash
   oc get deployment todo-frontend -o yaml | grep REACT_APP_API_URL
   ```

### Route Access Issues

Verify route is created and has the correct host:

```bash
oc get route todo -n todo
```

Test route accessibility:

```bash
curl -k https://$(oc get route todo -n todo -o jsonpath='{.spec.host}')
```

## Upgrade

```bash
helm upgrade todo ./charts/applications/productivity/todo \
  --namespace todo \
  --reuse-values
```

## Uninstall

```bash
helm uninstall todo --namespace todo
```

**Note**: PVCs are not automatically deleted. To remove data:

```bash
oc delete pvc -n todo todo-backend-data
```

## Contributing

This chart follows the standards defined in `docs/CHART-STANDARDS.md`.

## References

- [Source Repository](https://github.com/jgough-essextec/the_petri_dish)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Chart Standards](../../../docs/CHART-STANDARDS.md)
