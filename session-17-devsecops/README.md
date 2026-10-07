# Session 17: Complete CI/CD & DevSecOps

## DevSecOps Demo Project

This project demonstrates a full CI/CD pipeline integrated with modern DevSecOps tooling.

### CI/CD Pipeline
- **Application Build:** Successfully compiled and built the application.
- **Unit Testing:** Executed unit tests in the pipeline.
- **Docker Image Build:** Created a container image from the Dockerfile.
- **Container Registry:** Pushed the image to a container registry.
- **Kubernetes Deployment:** Automatically updated the manifests and deployed to Kubernetes.

### Security Implementation
- **SAST (Static Application Security Testing):** Analyzed the source code for vulnerabilities during the build phase.
- **SCA (Software Composition Analysis):** Scanned third-party dependencies for known CVEs.
- **Secret Scanning:** Integrated checks to prevent hardcoded passwords and API keys from entering the repository.
- **Container Image Scanning:** Scanned the Docker image using Trivy before pushing.
- **Security Gates:** The pipeline is configured to fail the build if high or critical vulnerabilities are discovered.

### Deliverables Included
- **Application Code & Dockerfile**
- **GitHub Actions Workflow YAML**
- **Kubernetes Deployment Manifests**
- **Pipeline Execution Screenshots (Refer to GitHub Actions tab)**
