#!/usr/bin/env python3
"""Run Session 17 tests, real security scans, build, and local Kubernetes rollout.

Publishing and GitHub Actions execution are separate steps requiring approval.
SECURITY_ENV selects the virtual environment containing the pinned Python tools.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lab_evidence import CONTEXT, ROOT, Evidence

SESSION = "session-17-devsecops"
APP = ROOT / SESSION / "demo"
BIN = Path(os.environ.get("SECURITY_ENV", "/private/tmp/devops-security-venv")) / "bin"
TOOLS = APP / ".tools" / "bin"
REPORTS = APP / "reports"
REPORTS.mkdir(exist_ok=True)
os.environ["COVERAGE_FILE"] = str(REPORTS / ".coverage")
os.environ["SEMGREP_SEND_METRICS"] = "off"
os.environ["TRIVY_CACHE_DIR"] = "/private/tmp/devops-trivy-cache"
os.environ["DOCKER_HOST"] = subprocess.check_output(
    ["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"], text=True).strip()

e = Evidence(SESSION, "00-tools", "Session 17 - pinned scanner versions")
for cmd in [[str(BIN / "python"), "--version"], [str(BIN / "semgrep"), "--version"],
            [str(TOOLS / "gitleaks"), "version"], [str(TOOLS / "trivy"), "--version"]]:
    e.run(cmd, cwd=APP)

e = Evidence(SESSION, "01-tests", "Session 17 - actual build and unit test output")
e.run([str(BIN / "python"), "-c", "import ast,pathlib; files=list(pathlib.Path('app').rglob('*.py')); [ast.parse(p.read_text()) for p in files]; print(f'{len(files)} Python source files parsed successfully')"], cwd=APP)
e.run([str(BIN / "pytest"), "-v", "--cov=app", "--cov-report=term-missing", "--cov-report=xml:reports/coverage.xml", "--junitxml=reports/tests.xml", "-o", "cache_dir=reports/pytest-cache"], cwd=APP)

e = Evidence(SESSION, "02-sast", "SAST - real Semgrep Python and JavaScript rules")
e.run([str(BIN / "semgrep"), "scan", "--config", "p/python", "--config", "p/javascript", "--error", "--metrics", "off", "--json-output", "reports/sast.json", "app"], cwd=APP, timeout=300)

e = Evidence(SESSION, "03-secret-scan", "Secret scanning - real Gitleaks scan of the demo source tree")
e.run([str(TOOLS / "gitleaks"), "dir", "--redact", "--report-format", "json", "--report-path", "reports/secrets.json", "."], cwd=APP, timeout=180)

e = Evidence(SESSION, "04-sca", "SCA - real vulnerability audit of pinned runtime dependencies")
e.run([str(BIN / "pip-audit"), "-r", "requirements.txt", "--strict", "--format", "json", "--output", "reports/sca.json"], cwd=APP, timeout=300)
sca = json.loads((REPORTS / "sca.json").read_text())
e.note(f"Audited {len(sca['dependencies'])} runtime dependencies; vulnerabilities: {sum(len(d['vulns']) for d in sca['dependencies'])}")

content = hashlib.sha256()
for p in sorted(APP.rglob("*")):
    if p.is_file() and ("app" in p.relative_to(APP).parts or p.name in {"Dockerfile", "requirements.txt"}) and "__pycache__" not in p.parts:
        content.update(str(p.relative_to(APP)).encode())
        content.update(p.read_bytes())
tag = "session17-homework:local-" + content.hexdigest()[:12]
e = Evidence(SESSION, "05-image-scan", "Docker build and real Trivy HIGH/CRITICAL vulnerability gate")
e.run(["docker", "build", "--pull", "-t", tag, "."], cwd=APP, timeout=600)
e.run([str(TOOLS / "trivy"), "image", "--scanners", "vuln", "--severity", "HIGH,CRITICAL", "--exit-code", "1", "--format", "json", "--output", "reports/image.json", tag], cwd=APP, timeout=600)
report = json.loads((REPORTS / "image.json").read_text())
e.note(f"Image: {tag}")
e.note(f"HIGH/CRITICAL vulnerabilities: {sum(len(x.get('Vulnerabilities', [])) for x in report.get('Results', []))}")
e.run(["docker", "image", "inspect", tag, "--format", "Image ID: {{.Id}}; runtime user: {{.Config.User}}"], cwd=APP)

e = Evidence(SESSION, "06-kubernetes", "Session 17 - local Kubernetes deployment and live HTTP checks")
e.run(["kind", "load", "docker-image", tag, "--name", "session13"], cwd=APP, timeout=180)
e.k("session17-homework", "create", "namespace", "session17-homework", check=False)
manifest = (APP / "k8s" / "deployment.yaml").read_text().replace("ghcr.io/suhassk205/devops-devsecops:__IMAGE_TAG__", tag)
e.k("session17-homework", "apply", "-f", "-", input=manifest)
e.k("session17-homework", "apply", "-f", str(APP / "k8s" / "service.yaml"))
e.k("session17-homework", "rollout", "status", "deployment/session17-python", "--timeout=120s")
e.k("session17-homework", "get", "pods", "-o", "wide")
e.k("session17-homework", "get", "service", "session17-python")
e.k("session17-homework", "exec", "deployment/session17-python", "--", "python", "-c",
    "import json,urllib.request; root='http://session17-python'; health=json.load(urllib.request.urlopen(root+'/health')); assert health['status']=='healthy'; print('Health:',health); print('API:',json.load(urllib.request.urlopen(root+'/api/status')))" )
e.note("Local verification complete. Registry publication and hosted GitHub Actions execution remain pending push approval.")
print("Session 17 local verification complete.", flush=True)
