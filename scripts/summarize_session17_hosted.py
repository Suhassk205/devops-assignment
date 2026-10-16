#!/usr/bin/env python3
"""Summarize downloaded GitHub Actions reports without rerunning the scans."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1] / "session-17-devsecops/evidence/hosted-reports"
run = json.loads((root / "run.json").read_text())
assert run["conclusion"] == "success"
print("GitHub Actions run:", run["url"])
print("Commit:", run["headSha"])
print("Jobs:", len(run["jobs"]), "successful")
for job in run["jobs"]:
    assert job["conclusion"] == "success"
    print("  PASS:", job["name"])

sast = json.loads((root / "sast-report/sast.json").read_text())
sca = json.loads((root / "sca-report/sca.json").read_text())
secrets = json.loads((root / "secret-scan-report/secrets.json").read_text())
image = json.loads((root / "image-scan-report/image.json").read_text())
suite = ET.parse(root / "test-reports/tests.xml").getroot().find("testsuite")
assert int(suite.attrib["failures"]) == 0 and int(suite.attrib["errors"]) == 0
assert not sast["results"] and not sast["errors"]
assert not any(d["vulns"] for d in sca["dependencies"])
assert not secrets
assert not any(r.get("Vulnerabilities", []) for r in image.get("Results", []))
print("\nUnit tests:", suite.attrib["tests"], "passed")
print("Semgrep: 0 findings, 0 errors")
print("pip-audit:", len(sca["dependencies"]), "runtime dependencies, 0 vulnerabilities")
print("Gitleaks: 0 findings")
print("Trivy: 0 HIGH/CRITICAL vulnerabilities")
print("Scanned image:", image["ArtifactName"])

for name in ["health.json", "status.json"]:
    data = json.loads((root / "deployment-evidence" / name).read_text())
    assert data["status"] in {"healthy", "running"}
    print(name + ":", data["status"])

print("\nKubernetes Pods:")
print((root / "deployment-evidence/pods.txt").read_text().strip())
print("\nKubernetes Service:")
print((root / "deployment-evidence/services.txt").read_text().strip())
