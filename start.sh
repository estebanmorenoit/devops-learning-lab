#!/usr/bin/env bash
set -euo pipefail

echo ""
echo "  ╔════════════════════════════════════════════════╗"
echo "  ║   DevOps Learning Lab v3                       ║"
echo "  ║   Real k3s · ArgoCD · ESO · Prometheus         ║"
echo "  ╚════════════════════════════════════════════════╝"
echo ""

if ! command -v docker &>/dev/null; then
    echo "  ERROR: docker not found."
    exit 1
fi

ACTION=${1:-up}

case "$ACTION" in
    up)
        # Start without forcing a rebuild — images are built on first run automatically.
        # Run './start.sh build' to force a rebuild after Dockerfile changes.
        docker compose up -d
        echo ""
        echo "  ✓ Frontend:  http://localhost:3000"
        echo ""
        echo "  ⏳ First run: k3s + ArgoCD + ESO + Prometheus are bootstrapping."
        echo "     Takes 3-5 minutes. Cluster status turns green in the UI when ready."
        echo ""
        echo "  Watch progress: ./start.sh logs-bootstrap"
        echo "  ArgoCD UI:      ./start.sh argocd-ui"
        echo "  Grafana UI:     ./start.sh grafana-ui"
        echo "  Stop:           ./start.sh stop"
        ;;
    build)
        # Rebuild images from scratch (needed after Dockerfile or requirements changes).
        docker compose up --build -d
        echo ""
        echo "  ✓ Rebuilt and started. Frontend: http://localhost:3000"
        ;;
    stop)
        docker compose down
        echo "  Stopped. State preserved in Docker volumes."
        echo "  Full reset: ./start.sh reset"
        ;;
    reset)
        docker compose down -v
        rm -f data/.bootstrap-done 2>/dev/null || true
        echo "  Cluster wiped. Run ./start.sh to rebuild."
        ;;
    logs)            docker compose logs -f backend frontend ;;
    logs-bootstrap)  docker compose logs -f bootstrap ;;
    logs-k3s)        docker compose logs -f k3s ;;
    restart)         docker compose restart backend ;;
    shell)           docker compose exec backend bash ;;
    argocd-ui)
        echo "  ArgoCD: http://localhost:8080"
        PASS=$(cat data/argocd-password 2>/dev/null || echo "")
        [ -n "$PASS" ] && echo "  Pass:   $PASS" || echo "  (bootstrap still running — check ./start.sh logs-bootstrap)"
        docker compose exec -d backend \
            kubectl port-forward svc/argocd-server -n argocd 8080:80 --address 0.0.0.0 || true
        ;;
    grafana-ui)
        echo "  Grafana: http://localhost:3001  (admin / prom-operator)"
        docker compose exec -d backend \
            kubectl port-forward svc/monitoring-grafana -n monitoring 3001:80 --address 0.0.0.0 || true
        ;;
    *)
        echo "  Usage: ./start.sh [up|build|stop|reset|logs|logs-bootstrap|shell|argocd-ui|grafana-ui]"
        echo ""
        echo "    up              Start the lab (build images only if not yet built)"
        echo "    build           Force rebuild images, then start"
        echo "    stop            Stop containers, preserve cluster state"
        echo "    reset           Wipe cluster and all state, start fresh"
        echo "    logs            Tail backend + frontend logs"
        echo "    logs-bootstrap  Tail cluster bootstrap logs"
        echo "    shell           Open a bash shell in the backend container"
        echo "    argocd-ui       Port-forward ArgoCD UI to http://localhost:8080"
        echo "    grafana-ui      Port-forward Grafana to http://localhost:3001"
        exit 1
        ;;
esac
