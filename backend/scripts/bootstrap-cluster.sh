#!/usr/bin/env bash
# Bootstrap script: installs ArgoCD, ESO, and sample workloads into k3s
# Runs once after k3s is healthy. Idempotent — safe to re-run.

set -euo pipefail

# The kubeconfig k3s writes has server: https://127.0.0.1:6443 which is only
# reachable from inside the k3s container itself. Patch it to use the Docker
# service name so this container (and the backend) can reach the API server.
until [ -f /etc/rancher/k3s/k3s.yaml ]; do sleep 1; done
cp /etc/rancher/k3s/k3s.yaml /tmp/k3s.yaml
sed -i 's|https://127.0.0.1:6443|https://k3s:6443|g' /tmp/k3s.yaml
export KUBECONFIG=/tmp/k3s.yaml

DONE_FLAG=/data/.bootstrap-done

GREEN="\033[32m" YELLOW="\033[33m" CYAN="\033[36m" GRAY="\033[90m" RESET="\033[0m"

log()  { echo -e "${CYAN}[bootstrap]${RESET} $*"; }
ok()   { echo -e "${GREEN}[bootstrap] ✓${RESET} $*"; }
skip() { echo -e "${GRAY}[bootstrap] →${RESET} $* (already done)"; }

# ── Wait for k3s API ──────────────────────────────────────────────────────────
log "Waiting for k3s API server..."
until kubectl cluster-info &>/dev/null; do
    sleep 2
done
ok "k3s API ready"

# ── Idempotency check ─────────────────────────────────────────────────────────
if [[ -f "$DONE_FLAG" ]]; then
    skip "Bootstrap already completed. Remove /data/.bootstrap-done to re-run."
    exit 0
fi

# ── Namespaces ────────────────────────────────────────────────────────────────
log "Creating namespaces..."
for ns in argocd monitoring harbor external-secrets learning; do
    kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f -
done
ok "Namespaces ready"

# ── ArgoCD ────────────────────────────────────────────────────────────────────
log "Installing ArgoCD..."
kubectl apply -n argocd \
    -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.10.5/manifests/install.yaml \
    --wait=false

# Patch to insecure mode (no TLS needed inside sandbox)
kubectl patch configmap argocd-cmd-params-cm -n argocd \
    --type merge \
    -p '{"data":{"server.insecure":"true"}}' 2>/dev/null || true

log "Waiting for ArgoCD server..."
kubectl rollout status deployment/argocd-server -n argocd --timeout=180s
ok "ArgoCD installed"

# ── ArgoCD CLI login ──────────────────────────────────────────────────────────
log "Configuring ArgoCD CLI..."
ARGOCD_PASSWORD=$(kubectl get secret argocd-initial-admin-secret \
    -n argocd -o jsonpath='{.data.password}' | base64 -d)

# Store for the terminal to use
echo "admin" > /data/argocd-user
echo "$ARGOCD_PASSWORD" > /data/argocd-password
cat > /data/argocd-env << EOF
ARGOCD_SERVER=argocd-server.argocd.svc.cluster.local:80
ARGOCD_AUTH_TOKEN=
ARGOCD_OPTS="--plaintext --port-forward-namespace argocd"
EOF
ok "ArgoCD password stored at /data/argocd-password"

# ── External Secrets Operator ─────────────────────────────────────────────────
log "Installing External Secrets Operator..."
helm repo add external-secrets https://charts.external-secrets.io --force-update
helm upgrade --install external-secrets external-secrets/external-secrets \
    -n external-secrets \
    --set installCRDs=true \
    --wait \
    --timeout=120s
ok "ESO installed"

# Wait for ESO CRDs to be registered and the controller to be ready
kubectl wait --for=condition=established --timeout=60s \
    crd/clustersecretstores.external-secrets.io \
    crd/externalsecrets.external-secrets.io
kubectl rollout status deployment/external-secrets -n external-secrets --timeout=60s
# API server discovery cache can lag behind CRD registration; poll until the
# new resource type is actually resolvable before trying to create resources.
until kubectl get clustersecretstores.external-secrets.io &>/dev/null; do sleep 2; done

# ── Sample ESO SecretStore (uses a fake AWS provider for learning) ─────────────
log "Creating sample ESO resources..."
kubectl apply -f - << 'EOF'
apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: fake-aws-secrets
spec:
  provider:
    fake:
      data:
        - key: "prod/db/password"
          value: "supersecret-db-password-123"
          version: "v1"
        - key: "prod/harbor/robot-token"
          value: "robot-token-abc123xyz"
          version: "v1"
        - key: "prod/api/key"
          value: "api-key-prod-xyz789"
          version: "v1"
        - key: "prod/keycloak/admin"
          value: "keycloak-admin-pass-456"
          version: "v1"
EOF

kubectl apply -f - << 'EOF'
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: default
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: fake-aws-secrets
    kind: ClusterSecretStore
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: "prod/db/password"
EOF

kubectl apply -f - << 'EOF'
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: harbor-robot-token
  namespace: learning
spec:
  refreshInterval: 24h
  secretStoreRef:
    name: fake-aws-secrets
    kind: ClusterSecretStore
  target:
    name: harbor-robot-token
  data:
    - secretKey: token
      remoteRef:
        key: "prod/harbor/robot-token"
EOF
ok "ESO resources created"

# ── Prometheus stack (lightweight) ────────────────────────────────────────────
log "Installing kube-prometheus-stack (this takes a minute)..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
    -n monitoring \
    --set prometheus.prometheusSpec.retention=2h \
    --set prometheus.prometheusSpec.resources.requests.memory=256Mi \
    --set prometheus.prometheusSpec.resources.limits.memory=512Mi \
    --set prometheus.prometheusSpec.externalLabels.cluster=devops-sandbox \
    --set alertmanager.enabled=true \
    --set grafana.enabled=true \
    --set grafana.adminPassword=admin \
    --set grafana.resources.requests.memory=128Mi \
    --set nodeExporter.enabled=false \
    --timeout=300s \
    --wait
ok "Prometheus + Grafana installed"

# ── Sample workloads for exercises ───────────────────────────────────────────
log "Deploying sample workloads..."

# Healthy app
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: default
  labels:
    app: web-app
    version: v1.2.3
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
        version: v1.2.3
    spec:
      containers:
      - name: web-app
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 50m
            memory: 32Mi
          limits:
            memory: 64Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
  namespace: default
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
EOF

# Crash-looping app (for debugging exercises)
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-app
  namespace: default
  labels:
    app: broken-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: broken-app
  template:
    metadata:
      labels:
        app: broken-app
    spec:
      containers:
      - name: broken-app
        image: busybox:1.36
        command: ["/bin/sh", "-c", "echo 'Starting...'; sleep 5; echo 'ERROR: DB connection failed'; exit 1"]
        resources:
          requests:
            cpu: 10m
            memory: 16Mi
          limits:
            memory: 32Mi
EOF

# Learning namespace workloads
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: learning
  labels:
    app: api-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api-server
        image: hashicorp/http-echo:1.0
        args: ["-text=Hello from api-server v1.0.0", "-listen=:8080"]
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 10m
            memory: 16Mi
          limits:
            memory: 32Mi
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: learning
data:
  environment: "sandbox"
  region: "eu-central-1"
  log_level: "info"
  db_host: "postgres.learning.svc.cluster.local"
EOF

ok "Sample workloads deployed"

# ── ArgoCD sample applications ────────────────────────────────────────────────
log "Creating ArgoCD sample applications..."

# Get admin password again for argocd CLI
ARGOCD_PWD=$(kubectl get secret argocd-initial-admin-secret \
    -n argocd -o jsonpath='{.data.password}' | base64 -d)

# Wait for argocd-server to be fully ready
kubectl wait --for=condition=available deployment/argocd-server \
    -n argocd --timeout=120s

# Register apps via kubectl (avoids needing argocd CLI auth in bootstrap)
kubectl apply -f - << 'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: false
      selfHeal: false
EOF

kubectl apply -f - << 'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: monitoring-stack
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: helm-guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  syncPolicy: {}
EOF

ok "ArgoCD applications created"

# ── PodDisruptionBudget example (for k8s exercises) ──────────────────────────
kubectl apply -f - << 'EOF'
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
  namespace: default
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: web-app
EOF

# ── Sample Prometheus alert rule ──────────────────────────────────────────────
kubectl apply -f - << 'EOF'
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: devops-learning-alerts
  namespace: monitoring
  labels:
    release: monitoring
spec:
  groups:
  - name: pod-health
    interval: 30s
    rules:
    - alert: PodCrashLooping
      expr: increase(kube_pod_container_status_restarts_total[15m]) > 3
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "Pod {{ $labels.pod }} is crash looping"
        description: "{{ $labels.pod }} in {{ $labels.namespace }} restarted {{ $value | humanize }} times"
    - alert: PodNotReady
      expr: kube_pod_status_ready{condition="true"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Pod {{ $labels.pod }} not ready for 5 minutes"
EOF

ok "PrometheusRule created"

# ── Write completion flag ─────────────────────────────────────────────────────
date > "$DONE_FLAG"
log ""
ok "Bootstrap complete!"
log "  ArgoCD:    kubectl port-forward svc/argocd-server -n argocd 8080:80"
log "  Grafana:   kubectl port-forward svc/monitoring-grafana -n monitoring 3001:80"
log "  Password:  admin / $(cat /data/argocd-password)"
