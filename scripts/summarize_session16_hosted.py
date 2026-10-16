#!/usr/bin/env python3
"""Summarize downloaded GitHub Actions results without inventing output."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1] / "session-16-github-actions/evidence"
run = json.loads((BASE / "hosted-run.json").read_text())
assert run["status"] == "completed" and run["conclusion"] == "success"
assert len(run["jobs"]) == 4 and all(job["conclusion"] == "success" for job in run["jobs"])
report = next((BASE / "hosted-reports").rglob("tests.xml"))
root = ET.parse(report).getroot()
suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
failures = sum(int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0)) for suite in suites)
assert tests == 15 and failures == 0
http = next((BASE / "hosted-reports").rglob("http-checks.txt")).read_text()
assert "'status': 'healthy'" in http and "'result': 15.0" in http
deployment = next((BASE / "hosted-reports").rglob("deployment.txt")).read_text()
assert sum("1/1" in line and "Running" in line for line in deployment.splitlines()) == 2
print("Run:", run["url"])
print("Source commit:", run["headSha"])
for job in run["jobs"]:
    print("PASS:", job["name"])
print(f"Tests: {tests} passed; {failures} failures/errors")
print("\nHosted Kubernetes deployment:")
print(deployment.strip())
print("\nHosted Service verification:")
print(http.strip())
