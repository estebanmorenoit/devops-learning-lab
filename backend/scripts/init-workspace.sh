#!/usr/bin/env bash
# Create sample files in /workspace for exercises

set -euo pipefail
WORKSPACE=/workspace
mkdir -p "$WORKSPACE/helm-charts/my-app/templates"

cat > "$WORKSPACE/app.log" << 'EOF'
2025-05-09T10:23:41Z level=info  msg="Starting application" version="1.2.3" port=8080
2025-05-09T10:23:41Z level=info  msg="Connected to database" host="postgres.default.svc" latency="12ms"
2025-05-09T10:23:42Z level=info  msg="Ready to serve traffic"
2025-05-09T10:24:01Z level=warn  msg="Slow response detected" path="/api/users" latency="2.1s"
2025-05-09T10:24:15Z level=error msg="Connection pool exhausted" pool_size=10
2025-05-09T10:25:01Z level=error msg="OOMKilled: container exceeded memory limit 512Mi"
2025-05-09T10:25:01Z level=error msg="Exiting" code=137
2025-05-09T10:25:10Z level=info  msg="Starting application" version="1.2.3" port=8080
2025-05-09T10:25:11Z level=warn  msg="Database connection slow" latency="850ms"
2025-05-09T10:25:15Z level=info  msg="Ready to serve traffic"
EOF

cat > "$WORKSPACE/pod.log" << 'EOF'
2025-05-09T10:00:00Z Pulling image "my-registry/my-app:latest"
2025-05-09T10:00:05Z Successfully pulled image "my-registry/my-app:latest"
2025-05-09T10:00:06Z Started container my-app
2025-05-09T10:00:06Z level=error msg="Failed to connect to DB: connection refused"
2025-05-09T10:00:07Z BackOff: Back-off restarting failed container
2025-05-09T10:05:00Z BackOff: Back-off restarting failed container
2025-05-09T10:15:00Z CrashLoopBackOff: container is in CrashLoopBackOff
EOF

cat > "$WORKSPACE/access.log" << 'EOF'
10.0.1.50 - - [09/May/2025:10:00:01 +0000] "GET /api/health HTTP/1.1" 200 42
10.0.2.101 - - [09/May/2025:10:00:02 +0000] "POST /api/users HTTP/1.1" 201 156
192.168.1.1 - - [09/May/2025:10:00:03 +0000] "GET /api/products HTTP/1.1" 200 1024
10.0.3.200 - - [09/May/2025:10:00:05 +0000] "DELETE /api/users/123 HTTP/1.1" 403 89
172.16.0.5 - - [09/May/2025:10:01:00 +0000] "GET /api/products HTTP/1.1" 500 256
10.0.2.102 - - [09/May/2025:10:01:01 +0000] "POST /api/login HTTP/1.1" 401 45
EOF

cat > "$WORKSPACE/config.yaml" << 'EOF'
# Application configuration
app:
  name: my-app
  version: 1.2.3
  environment: production
  port: 8080

database:
  host: postgres.default.svc.cluster.local
  port: 5432
  name: myapp_prod

cache:
  host: redis-cache.default.svc.cluster.local
  port: 6379
  ttl: 3600

observability:
  metrics_port: 9090
  log_level: info
EOF

cat > "$WORKSPACE/values.yaml" << 'EOF'
replicaCount: 2

image:
  repository: my-registry/my-app
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: true
  host: my-app.example.com

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    memory: 256Mi

sidecar:
  image: busybox
  tag: "1.36.1"

redis:
  enabled: true
  tag: latest

nginx:
  image: nginx
EOF

cat > "$WORKSPACE/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: default
  labels:
    app: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-registry/my-app:v1.2.3
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            memory: 256Mi
EOF

cat > "$WORKSPACE/requirements.txt" << 'EOF'
boto3==1.34.0
pyyaml==6.0.1
kubernetes==29.0.0
requests==2.31.0
click==8.1.7
rich==13.7.0
pytest==8.1.0
pytest-mock==3.14.0
EOF

cat > "$WORKSPACE/check_images.py" << 'PYEOF'
#!/usr/bin/env python3
"""Check Helm values for unpinned image tags."""
import argparse
import sys
import yaml
from pathlib import Path


def find_images(data, path=""):
    issues = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if key in ("tag", "image") and isinstance(value, str):
                if not value or value == "latest":
                    issues.append(f"  {current_path}: '{value}' — not pinned")
            else:
                issues.extend(find_images(value, current_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            issues.extend(find_images(item, f"{path}[{i}]"))
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("values_file", type=Path, nargs="?", default=Path("values.yaml"))
    parser.add_argument("--fail-on-issues", action="store_true")
    args = parser.parse_args()

    with open(args.values_file) as f:
        values = yaml.safe_load(f)

    issues = find_images(values)
    if not issues:
        print("✓ All image tags look good.")
    else:
        print(f"✗ Found {len(issues)} issue(s):")
        for issue in issues:
            print(issue)

    if args.fail_on_issues and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
PYEOF
chmod +x "$WORKSPACE/check_images.py"

echo "Workspace ready."
