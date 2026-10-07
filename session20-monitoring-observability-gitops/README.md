# Session 20: Monitoring, Observability & GitOps

This repository contains the proof of work for monitoring, observability, and GitOps deployments.

## Task 1: Monitoring with Prometheus & Grafana
We successfully deployed the Prometheus stack and configured Grafana to visualize metrics.

### Prometheus Up and Running
![Prometheus Dashboard](./03-prometheus/prometheus-up.png)

### Grafana Datasource Configuration
![Grafana Datasources](./04-grafana/grafana-datasource-added.png)

## Task 2: GitOps with ArgoCD
We integrated ArgoCD to achieve continuous reconciliation from our Git repository to the Kubernetes cluster.

### ArgoCD Dashboard Initialized
![ArgoCD Dashboard](./07-argocd/argocd-dashboard.png)

### Application Synced via GitOps
![ArgoCD Synced](./07-argocd/argocd-app-synced.png)
