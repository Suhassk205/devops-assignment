# Session 17: Complete CI/CD & DevSecOps

This exercise uses a [Flask dashboard](demo/README.md) to practice unit testing, security scanning, container builds, and Kubernetes deployment. The results below are from local tests and scans. The GitHub Actions workflow defines the same checks for CI.

## Application and delivery flow

```text
Flask dashboard -> build/tests -> Semgrep + pip-audit + Gitleaks
    -> Docker build -> Trivy gate -> preserve scanned image
    -> GHCR publication -> temporary Kind rollout -> live HTTP verification
```

The dashboard includes a pipeline simulator. Security checks run through the scanner tools and GitHub Actions workflow.

## Local test results

| Stage | Tool / implementation | Result |
|---|---|---|
| Source build and tests | Python source parsing; pytest + coverage | 8 tests passed; 69% statement coverage |
| SAST | Semgrep 1.181.0, `p/python` and `p/javascript` | 0 findings, 0 scan errors |
| Secret scanning | Gitleaks 8.30.1, default rules, redacted output | 0 findings in the demo source tree |
| SCA | pip-audit 2.10.1, pinned runtime requirements | 8 runtime dependencies audited; 0 known vulnerabilities |
| Container build | Python 3.12 Alpine base pinned by digest; Gunicorn | Image built; runtime user is UID 10001 |
| Image scanning | Trivy 0.76.0, HIGH/CRITICAL, `--exit-code 1` | 0 HIGH/CRITICAL vulnerabilities; no ignore-unfixed exception |
| Kubernetes | Deployment, Service, health probes and resource limits | 2 ready replicas; live `/health` and `/api/status` checks succeeded |
| Gate enforcement | Isolated intentionally unsafe fixtures | Semgrep, Gitleaks and pip-audit each returned exit 1 as required |

Rerun the scans before deployment, since vulnerability databases change. The local Gitleaks check scans the demo working tree; the CI job scans the repository’s Git history.

## Security changes

- Disabled Flask's development debugger; the container runs Gunicorn as a non-root user.
- Rendered the user-supplied pipeline branch with `textContent` instead of inserting it into HTML.
- Pinned runtime dependencies and the base image digest.
- Added an explicit secret-scanning job and strict vulnerability gates.
- Installed Trivy and Gitleaks from pinned official releases with SHA-256 verification.
- Configured readiness/liveness checks and restricted container privileges.

I also tested the security gates with separate examples containing debug-enabled Flask code, a dummy credential, and an old Flask dependency. Each scanner rejected its example with exit code 1. The redacted logs are linked below.

## GitHub Actions workflow

The [workflow](demo/.github/workflows/devsecops.yml) triggers on pushes to `main`, pull requests, and manual dispatch. Its dependency graph blocks image creation until tests, SAST, SCA and secret scanning pass. Trivy scans the built image before any publication.

The scanned image is saved as a workflow artifact; the publication job loads that same artifact rather than rebuilding. Only a push to `main` publishes. The deployment job pulls the published commit-SHA tag, loads it into a temporary Kind cluster, waits for rollout, and checks HTTP responses. The Kind cluster is created for the CI job and removed when the job ends.

GHCR authentication uses `GITHUB_TOKEN`, with package permissions set on the publish and deploy jobs. Test, scan, and deployment reports are uploaded as artifacts. To use the workflow in a separate repository, place the contents of `demo/` at its root.

## Run the local checks

From `demo/`, prepare an isolated Python environment with the pinned requirements and scanner tools described in [the demo README](demo/README.md). From the course repository root:

```bash
python3 scripts/run_session17.py
python3 scripts/verify_security_gates.py
```

The local script deploys into `session17-homework` on `kind-session13`.

## Recorded evidence

The text files contain the full command output; the screenshots show the main results.

| Exercise | Full output | Terminal screenshot |
|---|---|---|
| Session 17 - pinned scanner versions | [Transcript](evidence/00-tools.txt) | [Screenshot](screenshots/00-tools.png) |
| Session 17 - build and unit test output | [Transcript](evidence/01-tests.txt) | [Screenshot](screenshots/01-tests.png) |
| SAST - Semgrep Python and JavaScript rules | [Transcript](evidence/02-sast.txt) | [Screenshot](screenshots/02-sast.png) |
| Secret scanning - Gitleaks scan of the demo source tree | [Transcript](evidence/03-secret-scan.txt) | [Screenshot](screenshots/03-secret-scan.png) |
| SCA - vulnerability audit of pinned runtime dependencies | [Transcript](evidence/04-sca.txt) | [Screenshot](screenshots/04-sca.png) |
| Docker build and Trivy HIGH/CRITICAL vulnerability gate | [Transcript](evidence/05-image-scan.txt) | [Screenshot](screenshots/05-image-scan.png) |
| Session 17 - local Kubernetes deployment and live HTTP checks | [Transcript](evidence/06-kubernetes.txt) | [Screenshot](screenshots/06-kubernetes.png) |
| Security gates - deliberately unsafe fixtures must be rejected | [Transcript](evidence/07-security-gates.txt) | [Screenshot](screenshots/07-security-gates.png) |

### Selected screenshots

![01-tests](screenshots/01-tests.png)

![02-sast](screenshots/02-sast.png)

![05-image-scan](screenshots/05-image-scan.png)

![06-kubernetes](screenshots/06-kubernetes.png)

![07-security-gates](screenshots/07-security-gates.png)
