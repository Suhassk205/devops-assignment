# Session 17 DevSecOps dashboard

This Flask application provides a dashboard, health/status endpoints, greetings, calculator APIs and an on-page pipeline simulator. The simulator is separate from the real delivery pipeline.

## Local test results

Eight unit tests passed. Semgrep and Gitleaks reported no findings, pip-audit found no known vulnerabilities in the runtime dependencies, and Trivy found no HIGH/CRITICAL image vulnerabilities. Two local Kubernetes replicas passed the health and status checks. The [session README](https://github.com/Suhassk205/devops-assignment/blob/main/session-17-devsecops/README.md) includes the command output and screenshots.

## Run locally

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v --cov=app --cov-report=term-missing
gunicorn --bind 127.0.0.1:5001 --workers 2 app.app:app
```

Open `http://localhost:5001`. Direct development execution with `python app/app.py` binds only to localhost and leaves debugging disabled.

```bash
docker build -t session17-python:local .
docker run --rm -p 127.0.0.1:5001:5001 session17-python:local
```

The image runs Gunicorn as UID 10001. Runtime requirements and the Python base-image digest are pinned.

## API

| Method | Path | Behavior |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/health` | Application health |
| GET | `/api/status` | Runtime information |
| GET | `/api/greet/<name>` | Greeting |
| POST | `/api/add` | Addition |
| POST | `/api/calculate` | Calculator operations |
| POST | `/api/pipeline/run` | Simulated pipeline data |

## Security checks

```bash
pip install semgrep==1.181.0 pip-audit==2.10.1
python scripts/install_scanners.py
semgrep scan --config p/python --config p/javascript --error --metrics off app
.tools/bin/gitleaks dir --redact .
pip-audit -r requirements.txt --strict
.tools/bin/trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 session17-python:local
```

The installer supports macOS and Linux and verifies the official Trivy 0.76.0 / Gitleaks 8.30.1 release archive checksums. Generated tools, reports, caches and environments are ignored. CI uses Gitleaks on the application directory’s Git history; the local check uses the working tree.

The [session README](https://github.com/Suhassk205/devops-assignment/blob/main/session-17-devsecops/README.md) also includes tests of the failure gates. Separate examples with unsafe code, a dummy credential, and a vulnerable dependency were rejected with exit code 1.

## GitHub Actions

The course repository runs [.github/workflows/session17-devsecops.yml](../../.github/workflows/session17-devsecops.yml). The application stays in `session-17-devsecops/demo/`; the workflow configures that working directory for its commands.

```text
Build/tests -> Semgrep + pip-audit + Gitleaks -> Docker build
  -> Trivy -> scanned-image artifact -> GHCR -> temporary Kind -> HTTP checks
```

Pushes to `main` affecting the demo or workflow trigger the pipeline. Pull requests run the checks, and manual dispatch is available. Publication and deployment run on pushes to `main`. Images use `ghcr.io/suhassk205/devops-assignment/session17:COMMIT_SHA`.

The image is built once, scanned, and transferred as an artifact to the publish job. GitHub supplies `GITHUB_TOKEN`; package permissions are limited to the publish and deploy jobs. The deployment job creates a temporary Kind cluster, loads the published image, and checks the application's health and status endpoints.

## Kubernetes

The [Deployment](k8s/deployment.yaml) has two replicas, resource requests/limits, readiness/liveness checks and a non-root security context. The [Service](k8s/service.yaml) exposes port 80 and maps it to the application's port 5001.

For an image already published to an accessible registry:

```bash
kubectl set image --local -f k8s/deployment.yaml session17-python=ghcr.io/suhassk205/devops-assignment/session17:YOUR_COMMIT_SHA -o yaml | kubectl apply -f -
kubectl apply -f k8s/service.yaml
kubectl rollout status deployment/session17-python --timeout=180s
kubectl port-forward service/session17-python 5001:80
```

Replace the image tag before applying. Private registries require pull access; the CI job authenticates, pulls the image and loads it into Kind. The local course runner loads the checked local image into the named local cluster and uses its own namespace.
