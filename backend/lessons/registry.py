"""Lesson registry — ordered by the DevOps roadmap curriculum. Theory first, projects last."""

import json
from pathlib import Path
from typing import Optional

LESSONS_DIR = Path(__file__).parent / "content"

# Tuple: (phase, week, key, title, category, subdir)
# phase    → groups lessons in the sidebar and progress tracking
# week     → ordering within a phase
# key      → unique identifier and filename (content/<subdir>/<key>.json)
# title    → display name
# category → label shown in the UI
# subdir   → directory under content/
LESSON_ORDER = [
    # ── Linux & Operating System ──────────────────────────────────────────────
    ("linux",         1,  "linux-w1-fundamentals",    "Linux Fundamentals",                  "Linux",          "linux"),
    ("linux",         2,  "linux-w2-terminal",        "Terminal Mastery & System Monitoring", "Linux",          "linux"),
    # ── Version Control (Git) ─────────────────────────────────────────────────
    ("git",           1,  "git-w1-fundamentals",      "Git Fundamentals",                    "Git",            "git"),
    # ── Networking & Protocols ────────────────────────────────────────────────
    ("networking",    1,  "net-w1-protocols",         "Networking & Protocols",              "Networking",     "networking"),
    ("networking",    2,  "net-w1-tls",               "TLS, Certificates & PKI",             "Networking",     "networking"),
    ("networking",    3,  "net-w3-webservers",        "Web Servers, Reverse Proxies & Load Balancers", "Networking", "networking"),
    # ── Containers (Docker) ───────────────────────────────────────────────────
    ("docker",        1,  "docker-w1-fundamentals",   "Docker — Images, Layers & Networking","Docker",         "docker"),
    # ── Kubernetes ───────────────────────────────────────────────────────────
    ("kubernetes",    1,  "k8s-w1-core",              "Kubernetes Core Concepts",            "Kubernetes",     "kubernetes"),
    ("kubernetes",    2,  "k8s-w2-operations",        "Kubernetes Operations",               "Kubernetes",     "kubernetes"),
    # ── Cloud Providers ───────────────────────────────────────────────────────
    ("cloud",         1,  "cloud-w1-aws",             "Cloud Providers & AWS Fundamentals",  "Cloud",          "cloud"),
    # ── Infrastructure as Code ────────────────────────────────────────────────
    ("terraform",     1,  "tf-w1-modules",            "Terraform Modules & State",           "Terraform",      "terraform"),
    ("ansible",       1,  "ansible-w1-fundamentals",  "Configuration Management with Ansible","Ansible",       "ansible"),
    # ── CI/CD ─────────────────────────────────────────────────────────────────
    ("cicd",          1,  "cicd-w1-gitlab",           "GitLab CI/CD — Pipelines & Caching",  "CI/CD",          "cicd"),
    ("cicd",          2,  "cicd-w2-github-actions",   "CI/CD with GitHub Actions",           "CI/CD",          "cicd"),
    ("helm",          1,  "helm-w1-authoring",        "Helm Chart Authoring",                "Helm",           "helm"),
    # ── GitOps ───────────────────────────────────────────────────────────────
    ("gitops",        1,  "gitops-w1-argocd",         "GitOps & ArgoCD",                     "GitOps",         "gitops"),
    # ── Security (Secret Management) ─────────────────────────────────────────
    ("security",      1,  "sec-w1-secrets",           "Secret Management",                   "Security",       "security"),
    # ── Observability ─────────────────────────────────────────────────────────
    ("observability", 1,  "obs-w1-prometheus",        "Prometheus & PromQL",                 "Observability",  "observability"),
    ("observability", 2,  "obs-w2-logs",              "Logs Management",                     "Observability",  "observability"),
    # ── Bash Scripting ────────────────────────────────────────────────────────
    ("bash",          1,  "bash-w1-defensive",        "Defensive Bash Scripting",            "Bash",           "bash"),
    ("bash",          2,  "bash-w2-text",             "Text & Data Wrangling",               "Bash",           "bash"),
    ("bash",          3,  "bash-w3-idempotent",       "Idempotent Scripts & Functions",      "Bash",           "bash"),
    ("bash",          4,  "bash-w4-functions",        "Functions & Reusable Script Libraries","Bash",          "bash"),
    ("bash",          5,  "bash-w5-k8s",              "kubectl Scripting & Cluster Automation","Bash",         "bash"),
    ("bash-advanced", 1,  "bash-adv-w1-arrays",       "Arrays & Associative Arrays",         "Bash Advanced",  "bash-advanced"),
    ("bash-advanced", 2,  "bash-adv-w2-strings",      "Advanced String Processing",          "Bash Advanced",  "bash-advanced"),
    # ── Python Scripting ──────────────────────────────────────────────────────
    ("python",        1,  "python-w4-basics",         "Python Basics for DevOps",            "Python",         "python"),
    ("python",        2,  "python-w5-subprocess",     "subprocess & Error Handling",         "Python",         "python"),
    ("python",        3,  "python-w6-boto3",          "AWS Automation with boto3",           "Python",         "python"),
    ("python",        4,  "python-w7-kubernetes",     "Kubernetes Python Client",            "Python",         "python"),
    ("python",        5,  "python-w8-apis",           "REST APIs with requests",             "Python",         "python"),
    ("python-advanced",1, "py-adv-w1-classes",        "Classes & OOP for DevOps",            "Python Advanced","python-advanced"),
    ("python-advanced",2, "py-adv-w2-testing",        "Testing DevOps Scripts",              "Python Advanced","python-advanced"),
    # ── Projects ──────────────────────────────────────────────────────────────
    ("projects",      1,  "python-w9-gitlab",         "GitLab CI Helper Tool",               "Projects",       "python"),
    ("projects",      2,  "python-w10-eso",           "ESO Secret Rotation Tool",            "Projects",       "python"),
    ("projects",      3,  "python-w11-hygiene",       "Namespace & Cost Hygiene CLI",        "Projects",       "python"),
    ("projects",      4,  "python-w12-keycloak",      "Keycloak & On-Prem Ops",              "Projects",       "python"),
]


def get_all_lessons() -> list:
    return [
        {"key": key, "title": title, "phase": phase, "week": week, "category": cat}
        for phase, week, key, title, cat, subdir in LESSON_ORDER
    ]


def get_lesson(key: str) -> Optional[dict]:
    for phase, week, lkey, title, cat, subdir in LESSON_ORDER:
        if lkey == key:
            path = LESSONS_DIR / subdir / f"{key}.json"
            if path.exists():
                return json.loads(path.read_text())
    return None
