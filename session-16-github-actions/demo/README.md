# Session 16: Calculator CI and CD

This project keeps the original command-line calculator and adds a small HTTP service for the deployment exercise. GitHub Actions tests the code, checks for sensitive files, builds a container, and deploys that built image to a temporary Kubernetes cluster.

## Pipeline

```text
Push to main -> tests -> sensitive-file check -> application and Docker build
    -> container artifact -> Kubernetes deployment -> live HTTP checks
```

Pull requests run the CI checks and build. Deployment runs only after a push to `main`; the temporary cluster is removed when the hosted runner finishes.

| Job | Purpose |
|---|---|
| Test Application | Calculator tests and real HTTP request tests |
| Security Check | Reject `.env`, `.pem`, and `.key` files |
| Build Application and Image | Package source, build the container once, and upload artifacts |
| Deploy and Verify Application | Load that image into Kind, apply manifests, wait for two ready replicas, and check the Service |

The sensitive-file check is a basic classroom exercise. Session 17 covers dedicated security scanners.

## Files

- [Calculator](app/calculator.py): the original arithmetic functions and interactive CLI.
- [HTTP service](app/server.py): `/health` and `/calculate` endpoints.
- [Tests](tests/): arithmetic, HTTP responses, invalid input, and division by zero.
- [Dockerfile](Dockerfile): Python service running as UID 10001.
- [Workflow](.github/workflows/ci.yml): the CI and CD jobs.
- [Deployment](k8s/deployment.yaml): two replicas with health probes and resource limits.
- [Service](k8s/service.yaml): port 80 routed to application port 8080.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
bash build.sh
python -m app.server
```

In another terminal:

```bash
curl --fail http://localhost:8080/health
curl --fail 'http://localhost:8080/calculate?operation=add&a=10&b=5'
```

The health check returns `{"status": "healthy"}`. The calculation returns an `add` result of `15.0`. Supported operations are `add`, `subtract`, `multiply`, and `divide`. Invalid operands, missing parameters, and division by zero return HTTP 400.

To use the original CLI, run `python app/calculator.py`.

## Container and local deployment

```bash
docker build -t session16-calculator:local .
docker run --rm -p 127.0.0.1:8080:8080 session16-calculator:local
```

For a Kind cluster named `session13`:

```bash
kind load docker-image session16-calculator:local --name session13
kubectl --context kind-session13 create namespace session16-homework
kubectl --context kind-session13 -n session16-homework apply -f k8s/
kubectl --context kind-session13 -n session16-homework rollout status deployment/session16-calculator --timeout=180s
kubectl --context kind-session13 -n session16-homework get deployment,pods,service
kubectl --context kind-session13 -n session16-homework port-forward service/session16-calculator 8080:80
```

Use the same HTTP requests through the forwarded port. Remove the exercise afterward with `kubectl --context kind-session13 delete namespace session16-homework`.

## CI and CD behavior

The workflow runs on GitHub-hosted Ubuntu runners. Tests must pass before the sensitive-file check, and both must pass before the build. The build uploads `calculator-build` and a commit-tagged `calculator-image` artifact. CD downloads that image instead of rebuilding it, loads it into Kind, and substitutes its exact tag in the Deployment.

The CD checks call the deployed application's Service from a Pod and assert that `/health` is healthy and `10 + 5` returns 15. Deployment output, HTTP results, and application logs are uploaded as `deployment-reports`. Tests upload a JUnit report as `test-reports`.

This deployment uses the workflow's local container artifact, so it needs no registry credentials or AWS account. Workflow permissions are limited to reading repository contents. GitHub manages artifact access for the workflow.

## Local verification

All 15 tests passed. The container ran as UID 10001, two Kubernetes replicas became Ready, and the deployed Service returned the expected health and calculation responses. The temporary local namespace was removed after verification.

The [coursework submission README](https://github.com/Suhassk205/devops-assignment/blob/main/session-16-github-actions/README.md) contains the command output and screenshots.
