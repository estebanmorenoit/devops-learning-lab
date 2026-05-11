# DevOps Learning Lab

An interactive, self-hosted learning environment for DevOps engineers. Every lesson comes with a live browser terminal connected to a real k3s Kubernetes cluster — not a simulator. You run actual `kubectl`, `helm`, `argocd`, and Python commands against real infrastructure that boots inside Docker on your laptop.

## Architecture

![Architecture diagram](architecture.svg)

## Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Cluster | k3s | v1.29.4 | traefik, servicelb, metrics-server disabled |
| GitOps | ArgoCD | v2.10.5 | insecure mode (no TLS in sandbox) |
| Secrets | External Secrets Operator | latest chart | fake AWS provider pre-configured |
| Monitoring | kube-prometheus-stack | latest chart | Prometheus + Grafana + AlertManager |
| Backend | FastAPI + uvicorn | 0.111.0 / 0.29.0 | PTY WebSocket over `/ws/terminal/:id` |
| Frontend | nginx | alpine | SPA proxy, WebSocket upgrade |
| Terminal | xterm.js | 5.3.0 | xterm-addon-fit for auto-resize |
| Python libs | boto3, kubernetes, click, rich, requests, httpx, pytest | — | pre-installed in backend container |
| CLI tools | kubectl, helm, argocd | v1.29.4 / 3.x / v2.10.5 | available in every terminal session |

## Curriculum — 37 lessons across 14 topics

### Bash (weeks 1–3)
| # | Lesson | Key concepts |
|---|--------|-------------|
| 1 | Defensive Bash Scripting | `set -euo pipefail`, quoting, exit codes, traps |
| 2 | Text & Data Wrangling | `grep`, `sed`, `awk`, `jq`, log parsing |
| 3 | Idempotent Scripts & Functions | Guard conditions, lock files, retry loops |

### Python for DevOps (weeks 4–8)
| # | Lesson | Key concepts |
|---|--------|-------------|
| 4 | Python Basics for DevOps | File I/O, argparse, pathlib, json/yaml |
| 5 | subprocess & Error Handling | `subprocess.run`, capturing output, error propagation |
| 6 | AWS Automation with boto3 | EC2, S3, SSM, IAM with real-shaped mock responses |
| 7 | Kubernetes Python Client | `client.CoreV1Api()`, listing pods, watching events |
| 8 | REST APIs with requests | `requests`, `httpx`, pagination, retries, auth headers |

### Projects (weeks 9–12)
| # | Lesson | Description |
|---|--------|-------------|
| 9 | GitLab CI Helper Tool | CLI that queries GitLab API and summarises pipeline state |
| 10 | ESO Secret Rotation Tool | Triggers ESO refreshes and validates sync status |
| 11 | Namespace & Cost Hygiene CLI | Finds idle namespaces, unset resource limits, orphaned PVCs |
| 12 | Keycloak & On-Prem Ops | Keycloak admin API — user sync and realm management |

### Advanced & Specialist tracks
| Topic | Lessons | Covers |
|-------|---------|--------|
| Bash Advanced | Arrays, Advanced String Processing | Associative arrays, string ops, `mapfile`, `printf` |
| Python Advanced | Classes & OOP, Testing | Dataclasses, ABC, pytest, `pytest-mock`, monkeypatching |
| Networking | TLS, Certificates & PKI | x.509, `openssl`, cert rotation, K8s TLS secrets |
| Observability | Prometheus & PromQL | Metric types, labels, alerting rules, Grafana queries |
| GitLab CI/CD | Pipelines & Caching | Stages, artifacts, cache keys, `rules:`, `needs:` |
| Terraform | Modules & State | Module structure, remote state, `terraform import` |
| Helm | Chart Authoring | `values.yaml`, helpers, `_helpers.tpl`, chart testing |
| Docker | Images, Layers & Networking | Multi-stage builds, layer caching, bridge networks |

## Terminal sandbox

Each lesson opens a fully interactive bash shell inside the backend container. The environment is pre-configured for DevOps work:

```
esteban@sandbox:/workspace$
```

**Pre-installed tools:** `kubectl` `helm` `argocd` `python3` `boto3` `git` `jq` `curl` `openssl` `vim`

**Shell aliases:**

| Alias | Command |
|-------|---------|
| `k` | `kubectl` |
| `kgp` | `kubectl get pods` |
| `kgpa` | `kubectl get pods -A` |
| `kl` | `kubectl logs` |
| `kd` | `kubectl describe` |
| `kaf` | `kubectl apply -f` |
| `agl` | `argocd app list` |
| `ags` | `argocd app sync` |

**Workspace files** at `/workspace`:
- `app.log` — structured application log with errors, OOMKill, restarts
- `pod.log` — pod lifecycle log with CrashLoopBackOff sequence
- `access.log` — nginx access log with 4xx/5xx entries
- `deployment.yaml` — sample Kubernetes Deployment manifest
- `values.yaml` — Helm values file with intentionally unpinned image tags
- `config.yaml` — app config referencing cluster-internal services
- `check_images.py` — starter Python script (finds unpinned `latest` tags)

**Mock AWS environment** (for boto3 lessons):
```
AWS_DEFAULT_REGION=eu-central-1
AWS_ACCOUNT_ID=123456789012
AWS_PROFILE=prod
```

Run `help-devops` inside any terminal session for a quick command reference.

## Pre-installed cluster resources

The bootstrap container installs these on first start:

**ArgoCD** — two sample applications registered:
- `web-app` → syncs the ArgoCD guestbook example app
- `monitoring-stack` → tracks the helm-guestbook example

**External Secrets Operator** — `ClusterSecretStore` named `fake-aws-secrets` with four pre-seeded keys (fake values, for learning only):
```
prod/db/password          → <fake-db-password>
prod/harbor/robot-token   → <fake-robot-token>
prod/api/key              → <fake-api-key>
prod/keycloak/admin       → <fake-admin-password>
```

**Prometheus alerts** — two rules installed in the `monitoring` namespace:
- `PodCrashLooping` — fires when a pod restarts >3 times in 15 minutes
- `PodNotReady` — fires when a pod is not Ready for 5+ minutes

**Sample workloads:**
- `default/web-app` — 2-replica nginx deployment, healthy, behind a PodDisruptionBudget
- `default/broken-app` — intentionally crash-looping busybox (for debugging practice)
- `learning/api-server` — hashicorp/http-echo, used by Python and ESO lessons

## Requirements

- Docker with Compose v2 (`docker compose` subcommand)
- ~4 GB RAM free for k3s and the monitoring stack
- macOS, Linux, or Windows with WSL2

## Quick start

```bash
git clone https://github.com/estebanmorenoit/devops-learning-lab.git
cd devops-learning-lab
./start.sh build
```

Open **http://localhost:3000**. The cluster status indicator in the top-right turns green once k3s, ArgoCD, ESO, and Prometheus finish bootstrapping. **This takes 3–5 minutes on first run** while Helm charts are downloaded and deployed.

Watch bootstrap progress in a separate terminal:

```bash
./start.sh logs-bootstrap
```

## Commands

```bash
./start.sh                   # same as 'up'
./start.sh up                # build images and start all services
./start.sh stop              # stop containers, preserve volumes (fast restart)
./start.sh reset             # destroy volumes + bootstrap flag (full wipe)
./start.sh logs              # tail backend + frontend logs
./start.sh logs-bootstrap    # tail bootstrap logs (useful on first run)
./start.sh logs-k3s          # tail k3s control-plane logs
./start.sh restart           # restart only the backend container
./start.sh shell             # open an interactive bash shell in the backend
./start.sh argocd-ui         # port-forward ArgoCD → http://localhost:8080
./start.sh grafana-ui        # port-forward Grafana → http://localhost:3001 (admin/admin)
```

## Exposed ports

| Port | Service | Notes |
|------|---------|-------|
| 3000 | Frontend (nginx) | Main UI |
| 8000 | Backend (FastAPI) | API + WebSocket (also reachable directly) |
| 8080 | ArgoCD UI | Only after `./start.sh argocd-ui` |
| 3001 | Grafana | Only after `./start.sh grafana-ui` |
| 9090 | Prometheus | Manual port-forward: `kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090` |

ArgoCD admin password is written to `./data/argocd-password` by the bootstrap script.

## Persistence

Progress across lessons is saved to `./data/progress.json` on the host. Cluster state lives in the `k3s-server` Docker volume. Both survive `./start.sh stop` and are only removed by `./start.sh reset`.

## Resetting to a clean state

```bash
./start.sh reset   # removes Docker volumes and ./data/.bootstrap-done
./start.sh up      # rebuilds and re-bootstraps from scratch (~5 min)
```

## Project layout

```
devops-learning-lab/
├── start.sh                      # CLI wrapper for docker compose operations
├── docker-compose.yml            # Four services: k3s, bootstrap, backend, frontend
├── data/                         # Mounted into all containers; holds progress + argocd creds
├── backend/
│   ├── main.py                   # FastAPI app + PTY WebSocket handler
│   ├── requirements.txt          # fastapi, uvicorn, websockets
│   ├── Dockerfile                # Python 3.12, kubectl, helm, argocd, Python DevOps libs
│   ├── Dockerfile.bootstrap      # alpine/k8s image for one-shot cluster setup
│   ├── lessons/
│   │   ├── registry.py           # Ordered lesson list (22 entries)
│   │   └── content/              # One JSON file per lesson
│   │       ├── bash/             # bash-w1..w3
│   │       ├── bash-advanced/    # bash-adv-w1..w2
│   │       ├── python/           # python-w4..w12
│   │       ├── python-advanced/  # py-adv-w1..w2
│   │       ├── networking/
│   │       ├── observability/
│   │       ├── cicd/
│   │       ├── terraform/
│   │       ├── helm/
│   │       └── docker/
│   └── scripts/
│       ├── bootstrap-cluster.sh  # Installs ArgoCD, ESO, Prometheus; deploys sample workloads
│       ├── init-workspace.sh     # Populates /workspace with sample files
│       └── help-devops.sh        # In-terminal quick reference command
└── frontend/
    ├── index.html                # Single-page app: lesson viewer + xterm.js terminal
    ├── Dockerfile                # nginx alpine
    └── nginx.conf                # SPA routing + /api/ and /ws/ proxy to backend
```
