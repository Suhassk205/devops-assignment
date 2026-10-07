# Session 15: Helm Homework

## Task 1: Helm Commands

- `helm create <name>`: Scaffolds a new Helm chart directory structure.
- `helm install <release> <chart>`: Installs a Helm chart onto the cluster.
- `helm list`: Lists all deployed releases.
- `helm status <release>`: Shows the status, deployed resources, and notes of a release.
- `helm get all <release>`: Downloads and prints all the manifests and values generated for a release.
- `helm upgrade <release> <chart>`: Upgrades a release to a new version of a chart or applies new values.
- `helm history <release>`: Shows the revision history of a release.
- `helm rollback <release> <revision>`: Rolls back a release to a previous revision.
- `helm uninstall <release>`: Deletes a deployed release from the cluster.
- `helm repo add <name> <url>`: Adds a remote chart repository.
- `helm search repo <keyword>`: Searches repositories for charts.

## Task 2: Helm Rollback Workflow

1. **Install:** `helm install my-app ./my-chart`
2. **Upgrade:** Updated `values.yaml` image tag, then ran `helm upgrade my-app ./my-chart`.
3. **Verify:** `helm status my-app` (shows revision 2).
4. **Upgrade again:** Made another change and ran `helm upgrade my-app ./my-chart`.
5. **Verify:** `helm history my-app` (shows revision 3).
6. **Rollback:** `helm rollback my-app 1` (Rolls back to the first successful install).
7. **Verify:** `helm history my-app` (shows revision 4, which is identical to revision 1). The application is successfully restored.

## Task 3: Mini Project
The Helm mini project was completed. The custom chart, templates, and `values.yaml` were successfully packaged, installed, upgraded, and verified on the cluster.
