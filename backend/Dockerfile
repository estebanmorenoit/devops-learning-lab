# syntax=docker/dockerfile:1
FROM python:3.14-slim

# System tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    bash-completion \
    curl \
    wget \
    git \
    jq \
    vim \
    nano \
    less \
    unzip \
    zip \
    tar \
    gzip \
    grep \
    sed \
    gawk \
    procps \
    net-tools \
    iproute2 \
    netcat-openbsd \
    iptables \
    ufw \
    openssh-client \
    lsof \
    sysstat \
    traceroute \
    mtr-tiny \
    telnet \
    iputils-ping \
    dnsutils \
    openssl \
    ca-certificates \
    make \
    tree \
    file \
    findutils \
    diffutils \
    locales \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install kubectl
RUN curl -fsSL "https://dl.k8s.io/release/v1.29.4/bin/linux/$(dpkg --print-architecture)/kubectl" \
    -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    | HELM_INSTALL_DIR=/usr/local/bin bash

# Install ArgoCD CLI
RUN curl -fsSL -o /usr/local/bin/argocd \
    "https://github.com/argoproj/argo-cd/releases/download/v2.10.5/argocd-linux-$(dpkg --print-architecture)" \
    && chmod +x /usr/local/bin/argocd

# Install k9s (pinned version for reproducible builds)
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    curl -fsSL "https://github.com/derailed/k9s/releases/download/v0.32.5/k9s_Linux_${ARCH}.tar.gz" \
        | tar -xz -C /usr/local/bin k9s \
    && chmod +x /usr/local/bin/k9s

# Install Terraform
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    curl -fsSL "https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_${ARCH}.zip" \
        -o /tmp/terraform.zip \
    && unzip /tmp/terraform.zip terraform -d /usr/local/bin \
    && rm /tmp/terraform.zip

# Install Vault
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    curl -fsSL "https://releases.hashicorp.com/vault/1.17.6/vault_1.17.6_linux_${ARCH}.zip" \
        -o /tmp/vault.zip \
    && unzip /tmp/vault.zip vault -d /usr/local/bin \
    && rm /tmp/vault.zip

# Install Trivy
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    [ "$ARCH" = "amd64" ] && TRIVY_ARCH="64bit" || TRIVY_ARCH="ARM64"; \
    curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v0.70.0/trivy_0.70.0_Linux-${TRIVY_ARCH}.tar.gz" \
        | tar -xz -C /usr/local/bin trivy \
    && chmod +x /usr/local/bin/trivy

# Install kubeseal
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    curl -fsSL "https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.36.6/kubeseal-0.36.6-linux-${ARCH}.tar.gz" \
        | tar -xz -C /usr/local/bin kubeseal \
    && chmod +x /usr/local/bin/kubeseal

# Install eksctl
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    curl -fsSL "https://github.com/eksctl-io/eksctl/releases/download/v0.226.0/eksctl_Linux_${ARCH}.tar.gz" \
        | tar -xz -C /usr/local/bin eksctl \
    && chmod +x /usr/local/bin/eksctl

# Install dive
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    curl -fsSL "https://github.com/wagoodman/dive/releases/download/v0.13.1/dive_0.13.1_linux_${ARCH}.tar.gz" \
        | tar -xz -C /usr/local/bin dive \
    && chmod +x /usr/local/bin/dive

# Python DevOps libraries
RUN pip install --no-cache-dir \
    boto3 \
    pyyaml \
    kubernetes \
    requests \
    httpx \
    click \
    rich \
    tabulate \
    python-dotenv \
    jinja2 \
    pytest \
    pytest-mock \
    ansible \
    awscli \
    uv

# FastAPI backend
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Workspace and sample files
RUN mkdir -p /workspace /data

COPY scripts/init-workspace.sh /usr/local/bin/init-workspace
RUN chmod +x /usr/local/bin/init-workspace && /usr/local/bin/init-workspace

# help-devops command
COPY scripts/help-devops.sh /usr/local/bin/help-devops
RUN chmod +x /usr/local/bin/help-devops

# Bash config
RUN cat > /root/.bashrc << 'BASHRC'
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
shopt -s histappend

export PS1='\[\033[01;32m\]devops@sandbox\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

alias ls='ls --color=auto'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Kubernetes shortcuts
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgn='kubectl get nodes'
alias kgs='kubectl get svc'
alias kgd='kubectl get deploy'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias kaf='kubectl apply -f'
alias kdr='kubectl --dry-run=client -o yaml'

# ArgoCD shortcuts
alias agl='argocd app list'
alias ags='argocd app sync'
alias agg='argocd app get'

# AWS (mock — swap for real in prod)
alias awswho='aws sts get-caller-identity'

export KUBECONFIG=/tmp/k3s.yaml
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Bash completion
if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
fi

# kubectl completion
command -v kubectl &>/dev/null && source <(kubectl completion bash)
command -v helm    &>/dev/null && source <(helm completion bash)

echo ""
echo -e "\033[36m  DevOps Learning Sandbox\033[0m"
echo -e "\033[90m  Real k3s cluster | kubectl · helm · argocd · python3\033[0m"
echo -e "\033[90m  Workspace: /workspace | Type 'help-devops' for reference\033[0m"
echo ""

cd /workspace
BASHRC

COPY . .

EXPOSE 8000
# Patch the kubeconfig server URL from 127.0.0.1 (only reachable inside the
# k3s container) to the Docker service name before starting the API server.
CMD ["/bin/bash", "-c", "t=0; until [ -f /etc/rancher/k3s/k3s.yaml ]; do sleep 1; t=$((t+1)); [ $t -ge 180 ] && echo 'ERROR: timed out waiting for k3s kubeconfig' && exit 1; done && cp /etc/rancher/k3s/k3s.yaml /tmp/k3s.yaml && sed -i 's|https://127.0.0.1:6443|https://k3s:6443|g' /tmp/k3s.yaml && exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info"]
