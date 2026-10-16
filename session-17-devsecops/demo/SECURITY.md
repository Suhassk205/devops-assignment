# Security policy and classroom scope

The application is a learning demo with no authentication, persistent user accounts or production availability guarantees. Do not place real credentials in source files, screenshots, issues or scan logs.

The pipeline blocks on failing tests, Semgrep findings, vulnerable runtime dependencies, Gitleaks findings and HIGH/CRITICAL image vulnerabilities. Findings must be investigated and corrected rather than bypassed to obtain a passing screenshot.

Re-run the dependency and image scans before deployment because advisory databases change.

If a credential is exposed, revoke or rotate it at its provider and remove it from the repository/history as appropriate. Reports produced for secret scanning must remain redacted. Do not include the credential itself when reporting an issue.
