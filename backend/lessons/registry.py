"""Lesson registry — ordered by the DevOps roadmap curriculum. Theory first, projects last."""

import json
from pathlib import Path
from typing import Optional

LESSONS_DIR = Path(__file__).parent / "content"

# Tuple: (phase, week, key, title, category, subdir, difficulty)
# phase      → groups lessons in the sidebar and progress tracking
# week       → ordering within a phase
# key        → unique identifier and filename (content/<subdir>/<key>.json)
# title      → display name
# category   → label shown in the UI
# subdir     → directory under content/
# difficulty → beginner | intermediate | advanced
LESSON_ORDER = [
    # ── Linux & Operating System ──────────────────────────────────────────────
    ("linux",         1,  "linux-w1-fundamentals",    "Linux Fundamentals",                  "Linux",          "linux",          "beginner"),
    ("linux",         2,  "linux-w2-terminal",        "Terminal Mastery & System Monitoring", "Linux",          "linux",          "beginner"),
    # ── Version Control (Git) ─────────────────────────────────────────────────
    ("git",           1,  "git-w1-fundamentals",      "Git Fundamentals",                    "Git",            "git",            "beginner"),
    # ── Networking & Protocols ────────────────────────────────────────────────
    ("networking",    1,  "net-w1-protocols",         "Networking & Protocols",              "Networking",     "networking",     "beginner"),
    ("networking",    2,  "net-w1-tls",               "TLS, Certificates & PKI",             "Networking",     "networking",     "intermediate"),
    ("networking",    3,  "net-w3-webservers",        "Web Servers, Reverse Proxies & Load Balancers", "Networking", "networking", "intermediate"),
    # ── Containers (Docker) ───────────────────────────────────────────────────
    ("docker",        1,  "docker-w1-fundamentals",   "Docker — Images, Layers & Networking","Docker",         "docker",         "beginner"),
    # ── Kubernetes ───────────────────────────────────────────────────────────
    ("kubernetes",    1,  "k8s-w1-core",              "Kubernetes Core Concepts",            "Kubernetes",     "kubernetes",     "intermediate"),
    ("kubernetes",    2,  "k8s-w2-operations",        "Kubernetes Operations",               "Kubernetes",     "kubernetes",     "intermediate"),
    ("kubernetes",    3,  "k8s-w3-service-mesh",      "Service Mesh with Linkerd",           "Kubernetes",     "kubernetes",     "advanced"),
    # ── Cloud Providers ───────────────────────────────────────────────────────
    ("cloud",         1,  "cloud-w1-aws",             "Cloud Providers & AWS Fundamentals",  "Cloud",          "cloud",          "intermediate"),
    # ── Infrastructure as Code ────────────────────────────────────────────────
    ("terraform",     1,  "tf-w1-modules",            "Terraform Modules & State",           "Terraform",      "terraform",      "intermediate"),
    ("ansible",       1,  "ansible-w1-fundamentals",  "Configuration Management with Ansible","Ansible",       "ansible",        "intermediate"),
    # ── CI/CD ─────────────────────────────────────────────────────────────────
    ("cicd",          1,  "cicd-w1-gitlab",           "GitLab CI/CD — Pipelines & Caching",  "CI/CD",          "cicd",           "intermediate"),
    ("cicd",          2,  "cicd-w2-github-actions",   "CI/CD with GitHub Actions",           "CI/CD",          "cicd",           "intermediate"),
    ("helm",          1,  "helm-w1-authoring",        "Helm Chart Authoring",                "Helm",           "helm",           "intermediate"),
    # ── GitOps ───────────────────────────────────────────────────────────────
    ("gitops",        1,  "gitops-w1-argocd",         "GitOps & ArgoCD",                     "GitOps",         "gitops",         "intermediate"),
    # ── Security ─────────────────────────────────────────────────────────────
    ("security",      1,  "sec-w1-secrets",           "Secret Management",                   "Security",       "security",       "intermediate"),
    ("security",      2,  "sec-w2-rbac",              "Kubernetes RBAC",                     "Security",       "security",       "intermediate"),
    ("security",      3,  "sec-w3-network-policies",  "Network Policies",                    "Security",       "security",       "advanced"),
    # ── Observability ─────────────────────────────────────────────────────────
    ("observability", 1,  "obs-w1-prometheus",        "Prometheus & PromQL",                 "Observability",  "observability",  "intermediate"),
    ("observability", 2,  "obs-w2-logs",              "Logs Management",                     "Observability",  "observability",  "intermediate"),
    ("observability", 3,  "obs-w3-tracing",           "Distributed Tracing & OpenTelemetry", "Observability",  "observability",  "advanced"),
    # ── Bash Scripting ────────────────────────────────────────────────────────
    ("bash",          1,  "bash-w1-defensive",        "Defensive Bash Scripting",            "Bash",           "bash",           "beginner"),
    ("bash",          2,  "bash-w2-text",             "Text & Data Wrangling",               "Bash",           "bash",           "intermediate"),
    ("bash",          3,  "bash-w3-idempotent",       "Idempotent Scripts & Functions",      "Bash",           "bash",           "intermediate"),
    ("bash",          4,  "bash-w4-functions",        "Functions & Reusable Script Libraries","Bash",          "bash",           "intermediate"),
    ("bash",          5,  "bash-w5-k8s",              "kubectl Scripting & Cluster Automation","Bash",         "bash",           "advanced"),
    ("bash-advanced", 1,  "bash-adv-w1-arrays",       "Arrays & Associative Arrays",         "Bash Advanced",  "bash-advanced",  "advanced"),
    ("bash-advanced", 2,  "bash-adv-w2-strings",      "Advanced String Processing",          "Bash Advanced",  "bash-advanced",  "advanced"),
    # ── Python Scripting ──────────────────────────────────────────────────────
    ("python",        1,  "python-w4-basics",         "Python Basics for DevOps",            "Python",         "python",         "beginner"),
    ("python",        2,  "python-w5-subprocess",     "subprocess & Error Handling",         "Python",         "python",         "intermediate"),
    ("python",        3,  "python-w6-boto3",          "AWS Automation with boto3",           "Python",         "python",         "intermediate"),
    ("python",        4,  "python-w7-kubernetes",     "Kubernetes Python Client",            "Python",         "python",         "intermediate"),
    ("python",        5,  "python-w8-apis",           "REST APIs with requests",             "Python",         "python",         "intermediate"),
    ("python-advanced",1, "py-adv-w1-classes",        "Classes & OOP for DevOps",            "Python Advanced","python-advanced","advanced"),
    ("python-advanced",2, "py-adv-w2-testing",        "Testing DevOps Scripts",              "Python Advanced","python-advanced","advanced"),
    # ── Projects ──────────────────────────────────────────────────────────────
    ("projects",      1,  "python-w9-gitlab",         "GitLab CI Helper Tool",               "Projects",       "python",         "advanced"),
    ("projects",      2,  "python-w10-eso",           "ESO Secret Rotation Tool",            "Projects",       "python",         "advanced"),
    ("projects",      3,  "python-w11-hygiene",       "Namespace & Cost Hygiene CLI",        "Projects",       "python",         "advanced"),
    ("projects",      4,  "python-w12-keycloak",      "Keycloak & On-Prem Ops",              "Projects",       "python",         "advanced"),
]


def get_all_lessons() -> list:
    return [
        {
            "key": key,
            "title": title,
            "phase": phase,
            "week": i + 1,
            "category": cat,
            "difficulty": diff,
        }
        for i, (phase, week, key, title, cat, subdir, diff) in enumerate(LESSON_ORDER)
    ]


def get_lesson(key: str) -> Optional[dict]:
    for phase, week, lkey, title, cat, subdir, diff in LESSON_ORDER:
        if lkey == key:
            path = LESSONS_DIR / subdir / f"{key}.json"
            if path.exists():
                data = json.loads(path.read_text())
                data.setdefault("difficulty", diff)
                return data
    return None
