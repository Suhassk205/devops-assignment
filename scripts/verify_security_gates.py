#!/usr/bin/env python3
"""Prove security gates fail using isolated, deliberately unsafe test fixtures."""
from pathlib import Path
import tempfile
import hashlib
import os
from lab_evidence import ROOT, Evidence

APP = ROOT / "session-17-devsecops" / "demo"
BIN = Path(os.environ.get("SECURITY_ENV", "/private/tmp/devops-security-venv")) / "bin"
with tempfile.TemporaryDirectory(prefix="devops-negative-controls-") as directory:
    root = Path(directory)
    (root / "unsafe_flask.py").write_text('from flask import Flask\napp = Flask(__name__)\napp.run(debug=True)\n')
    e = Evidence("session-17-devsecops", "07-security-gates", "Security gates - deliberately unsafe fixtures must be rejected")
    e.note("Negative controls are temporary fixtures, separate from application code. Exit 1 is the required result for each control.")
    e.run([str(BIN / "semgrep"), "scan", "--config", "p/python", "--error", "--metrics", "off", "--no-git-ignore", str(root / "unsafe_flask.py")], cwd=APP, expected_exit=1, timeout=180)
    synthetic = "GITHUB_TOKEN=ghp_" + hashlib.sha256(b"nonfunctional scanner control").hexdigest()[:36]
    e.note("Gitleaks receives a generated, nonfunctional credential-shaped fixture on stdin. Findings are redacted.")
    e.run([str(APP / ".tools/bin/gitleaks"), "stdin", "--redact"], cwd=root, input=synthetic, expected_exit=1)
    (root / "vulnerable-requirements.txt").write_text("Flask==0.12\n")
    e.note("SCA control audits a deliberately old dependency version; it is not installed or used by the application.")
    e.run([str(BIN / "pip-audit"), "-r", str(root / "vulnerable-requirements.txt"), "--no-deps", "--disable-pip"], cwd=APP, expected_exit=1, timeout=180)
    e.note("Verified: all three deliberate findings returned exit 1 and would block the next CI stage.")
