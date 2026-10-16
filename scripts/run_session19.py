#!/usr/bin/env python3
"""Validate and test the Session 19 configuration without contacting AWS."""
from pathlib import Path
from lab_evidence import ROOT, Evidence

session = "session19-cloud-terraform"
project = ROOT / session / "08-mini-project"
context = "local Terraform; mocked AWS provider; no AWS resources created"

checks = Evidence(session, "01-terraform-validation", "Session 19: Terraform initialization and validation", context=context)
for args in [
    ["terraform", "version"],
    ["terraform", "init", "-backend=false", "-input=false", "-no-color"],
    ["terraform", "fmt", "-check", "-recursive"],
    ["terraform", "validate", "-no-color"],
]:
    checks.run(args, cwd=project, timeout=300)

tests = Evidence(session, "02-terraform-tests", "Session 19: local Terraform tests with a mocked AWS provider", context=context)
tests.run(["terraform", "test", "-no-color"], cwd=project, timeout=300)

plan = Evidence(session, "03-mocked-plan", "Session 19: mocked plan and test state", context=context)
plan.run(["terraform", "test", "-no-color", "-verbose"], cwd=project, timeout=300)
plan.note("This is a mocked-provider test. The plan and generated IDs are test data, not AWS deployment results.")
print("Session 19 validation and mocked-provider tests completed.")
