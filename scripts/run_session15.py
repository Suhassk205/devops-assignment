#!/usr/bin/env python3
"""Execute the Session 15 Helm lifecycle and mini-project, recording real output."""
import json
import sys
from pathlib import Path
from lab_evidence import CONTEXT, ROOT, Evidence, raw_k

SESSION = "session-15-helm"
BASE = ROOT / SESSION
NS = "session15-homework"


def helm(e, *args):
    return e.run(["helm", "--kube-context", CONTEXT, "--namespace", NS, *args], timeout=240)


def rollout(e, deployment):
    e.k(NS, "rollout", "status", "deployment/" + deployment, "--timeout=120s")


def image(e, deployment):
    return e.k(NS, "get", "deployment", deployment, "-o", r'jsonpath={.spec.template.spec.containers[0].image}{"\n"}')


START = int(sys.argv[1]) if len(sys.argv) > 1 else 0
chart = BASE / "07-install-upgrade" / "app-chart"

if START <= 0:
    e = Evidence(SESSION, "00-environment", "Session 15 - Helm and local cluster")
    e.run(["helm", "version", "--short"])
    e.run(["kubectl", "--context", CONTEXT, "get", "nodes"])
    e.k(NS, "create", "namespace", NS, check=False)
    chart = BASE / "practice" / "demo-chart"
    chart.parent.mkdir(parents=True, exist_ok=True)

if START <= 1:
    chart = BASE / "practice" / "demo-chart"
    e = Evidence(SESSION, "01-create-install", "Helm create, lint, install, list and status")
    if not chart.exists():
        e.run(["helm", "create", str(chart)])
    else:
        e.note("The practice chart already exists; preserving it for this rerun.")
    e.run(["helm", "lint", str(chart)])
    helm(e, "install", "demo-release", str(chart), "--set", "image.tag=1.27", "--wait", "--timeout", "180s")
    helm(e, "list")
    helm(e, "status", "demo-release")
    e.k(NS, "get", "pods", "-l", "app.kubernetes.io/instance=demo-release")


if START <= 2:
    e = Evidence(SESSION, "02-get", "Helm get - values and complete release details")
    helm(e, "get", "values", "demo-release")
    helm(e, "get", "all", "demo-release")


if START <= 3:
    e = Evidence(SESSION, "03-uninstall", "Helm uninstall - remove only the practice release")
    helm(e, "uninstall", "demo-release", "--wait")
    helm(e, "list")
    e.k(NS, "get", "pods", "-l", "app.kubernetes.io/instance=demo-release")


if START <= 4:
    e = Evidence(SESSION, "04-repository-search", "Helm repo and search commands")
    e.run(["helm", "repo", "add", "homework-examples", "https://helm.github.io/examples", "--force-update"])
    e.run(["helm", "repo", "update", "homework-examples"])
    e.run(["helm", "repo", "list"])
    e.run(["helm", "search", "repo", "homework-examples"])

    chart = BASE / "07-install-upgrade" / "app-chart"

if START <= 5:
    e = Evidence(SESSION, "05-revision-1", "Rollback exercise - install revision 1")
    helm(e, "install", "webapp", str(chart), "--set", "image.tag=1.24", "--wait", "--timeout", "180s")
    rollout(e, "webapp-app")
    assert "nginx:1.24" in image(e, "webapp-app")
    helm(e, "history", "webapp")


if START <= 6:
    e = Evidence(SESSION, "06-revision-2", "Rollback exercise - upgrade to revision 2")
    helm(e, "upgrade", "webapp", str(chart), "--set", "image.tag=1.25", "--wait", "--timeout", "180s")
    rollout(e, "webapp-app")
    assert "nginx:1.25" in image(e, "webapp-app")
    helm(e, "history", "webapp")


if START <= 7:
    e = Evidence(SESSION, "07-revision-3", "Rollback exercise - upgrade to revision 3")
    helm(e, "upgrade", "webapp", str(chart), "--set", "image.tag=1.27", "--wait", "--timeout", "180s")
    rollout(e, "webapp-app")
    assert "nginx:1.27" in image(e, "webapp-app")
    helm(e, "history", "webapp")


if START <= 8:
    e = Evidence(SESSION, "08-rollback-revision-4", "Rollback restores revision 1 configuration as revision 4")
    helm(e, "rollback", "webapp", "1", "--wait", "--timeout", "180s")
    rollout(e, "webapp-app")
    assert "nginx:1.24" in image(e, "webapp-app")
    history = json.loads(helm(e, "history", "webapp", "-o", "json"))
    assert history[-1]["revision"] == 4 and history[-1]["status"] == "deployed"
    helm(e, "history", "webapp")

    chart = BASE / "mini-project" / "notes-chart"

if START <= 9:
    chart = BASE / "mini-project" / "notes-chart"
    e = Evidence(SESSION, "09-mini-project-install", "Notes chart - lint, package and development deployment")
    e.run(["helm", "lint", str(chart)])
    package_dir = BASE / "packages"
    package_dir.mkdir(exist_ok=True)
    e.run(["helm", "package", str(chart), "--destination", str(package_dir)])
    helm(e, "install", "notes", str(package_dir / "notes-chart-0.1.0.tgz"), "--wait", "--timeout", "180s")
    rollout(e, "notes-deploy")
    e.k(NS, "get", "pods", "-l", "app=notes")
    e.k(NS, "get", "service", "notes-svc")
    e.k(NS, "exec", "deployment/notes-deploy", "--", "printenv", "APP_NAME", "ENVIRONMENT")
    e.k(NS, "exec", "deployment/webapp-app", "--", "curl", "--fail", "--retry", "10", "--retry-connrefused", "--retry-delay", "1", "-sI", "http://notes-svc")


if START <= 10:
    chart = BASE / "mini-project" / "notes-chart"
    e = Evidence(SESSION, "10-mini-project-upgrade", "Notes chart - production values and upgrade")
    helm(e, "upgrade", "notes", str(chart), "-f", str(chart / "values-prod.yaml"), "--wait", "--timeout", "180s")
    rollout(e, "notes-deploy")
    e.k(NS, "get", "pods", "-l", "app=notes")
    e.k(NS, "exec", "deployment/notes-deploy", "--", "printenv", "APP_NAME", "ENVIRONMENT")
    helm(e, "history", "notes")


if START <= 11:
    chart = BASE / "mini-project" / "notes-chart"
    e = Evidence(SESSION, "11-mini-project-rollback", "Notes chart - rollback and healthy final state")
    helm(e, "rollback", "notes", "1", "--wait", "--timeout", "180s")
    rollout(e, "notes-deploy")
    e.k(NS, "get", "pods", "-l", "app=notes")
    e.k(NS, "exec", "deployment/notes-deploy", "--", "printenv", "APP_NAME", "ENVIRONMENT")
    e.k(NS, "exec", "deployment/webapp-app", "--", "curl", "--fail", "--retry", "10", "--retry-connrefused", "--retry-delay", "1", "-sI", "http://notes-svc")
    helm(e, "history", "notes")
    helm(e, "list")
    print("Session 15 verification complete; webapp and notes remain healthy for inspection.", flush=True)
