# Manifests

This directory contains Kubernetes manifests and Helm charts for the DevOps Learning Lab. All files are designed to be realistic production examples — not minimal toy configs.

## Structure

```
manifests/
├── apps/                   # ArgoCD Application objects (GitOps entry points)
│   ├── web-app-argocd.yaml     # Single Application deploying the web-app workload
│   └── app-of-apps.yaml        # App of Apps pattern + ApplicationSet example
├── workloads/              # Kubernetes workload definitions
│   ├── web-app.yaml            # Deployment + Service + HPA + PDB (stateless app)
│   └── stateful-app.yaml       # StatefulSet + PVC + headless Service (PostgreSQL)
└── helm/
    └── my-chart/           # Full Helm chart with best-practice structure
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── _helpers.tpl
            ├── deployment.yaml
            ├── service.yaml
            └── configmap.yaml  # also includes ServiceAccount + HPA
```

## Quick Start

### Deploy the web app directly

```bash
kubectl apply -f manifests/workloads/web-app.yaml
kubectl get pods -n default -l app=web-app
```

### Deploy the stateful app (PostgreSQL)

```bash
kubectl apply -f manifests/workloads/stateful-app.yaml
kubectl get statefulsets,pvc -n default
```

### Install the Helm chart

```bash
# Dry-run first
helm install my-release manifests/helm/my-chart/ --dry-run

# Install
helm install my-release manifests/helm/my-chart/

# Override values
helm install my-release manifests/helm/my-chart/ \
  --set image.tag=v2.0.0 \
  --set replicaCount=3 \
  --set autoscaling.enabled=true

# Upgrade
helm upgrade my-release manifests/helm/my-chart/ --set image.tag=v2.1.0

# List releases
helm list

# Uninstall
helm uninstall my-release
```

### Set up GitOps with ArgoCD

```bash
# First, update the repoURL in apps/web-app-argocd.yaml to point to YOUR repo
# Then apply to register the Application with ArgoCD:
kubectl apply -f manifests/apps/web-app-argocd.yaml

# Watch ArgoCD sync it:
kubectl get applications -n argocd
argocd app list

# For the App of Apps pattern (manages all apps via GitOps):
kubectl apply -f manifests/apps/app-of-apps.yaml
```

## Key concepts demonstrated

| File | Concepts |
|------|----------|
| `workloads/web-app.yaml` | RollingUpdate strategy, dedicated ServiceAccount, liveness/readiness/startup probes, PodDisruptionBudget, HPA, topologySpreadConstraints |
| `workloads/stateful-app.yaml` | StatefulSet, headless Service, volumeClaimTemplates, stable pod identity, ConfigMap mounting |
| `apps/web-app-argocd.yaml` | ArgoCD Application, automated sync, prune/selfHeal options |
| `apps/app-of-apps.yaml` | App of Apps pattern, ApplicationSet with Git directory generator |
| `helm/my-chart/` | Chart structure, `_helpers.tpl`, conditional rendering, values overrides, HPA/SA via template |
