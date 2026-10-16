#!/usr/bin/env python3
"""Test, build, deploy, and verify the Session 16 calculator locally."""
from pathlib import Path
import json
import sys
from lab_evidence import Evidence, ROOT

SESSION = "session-16-github-actions"
DEMO = ROOT / SESSION / "demo"
NS = "session16-homework"
IMAGE = "session16-calculator:local"

if "--deploy" not in sys.argv:
    e = Evidence(SESSION, "01-tests-build", "Session 16 - application tests and container build")
    e.run([sys.executable, "-m", "pytest", "-v", "tests"], cwd=DEMO)
    e.run(["bash", "build.sh"], cwd=DEMO)
    e.run(["docker", "build", "-t", IMAGE, "."], cwd=DEMO)
    e.run(["docker", "image", "inspect", IMAGE, "--format", "Image: {{.Id}}; runtime user: {{.Config.User}}"])

e = Evidence(SESSION, "02-local-deployment", "Session 16 - local continuous deployment verification")
e.run(["kind", "load", "docker-image", IMAGE, "--name", "session13"])
e.k(NS, "create", "namespace", NS)
e.k(NS, "apply", "-f", str(DEMO / "k8s/deployment.yaml"))
e.k(NS, "apply", "-f", str(DEMO / "k8s/service.yaml"))
e.k(NS, "rollout", "status", "deployment/session16-calculator", "--timeout=180s")
e.k(NS, "get", "deployment,pods,service", "-o", "wide")
check = ('import json,time,urllib.request; base="http://session16-calculator"; '
         'health=json.load(urllib.request.urlopen(base+"/health", timeout=10)); '
         'result=json.load(urllib.request.urlopen(base+"/calculate?operation=add&a=10&b=5", timeout=10)); '
         'assert health["status"]=="healthy"; assert result["result"]==15; '
         'print("Health:",health); print("Calculation:",result)')
e.k(NS, "exec", "deployment/session16-calculator", "--", "python", "-c", check)
e.k(NS, "logs", "deployment/session16-calculator", "--tail=10")

e = Evidence(SESSION, "03-local-cleanup", "Session 16 - remove local deployment lab")
e.k(NS, "delete", "namespace", NS, "--wait=true", "--timeout=120s")
e.note("Verified: the local calculator deployment was removed after its HTTP checks passed.")
