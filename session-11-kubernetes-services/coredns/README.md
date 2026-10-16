# CoreDNS and Kubernetes Service Discovery

CoreDNS answers DNS queries for Kubernetes Services and selected Pod records. Its Kubernetes plugin watches API resources, so DNS records follow the cluster's declared Services and endpoints.

## Query flow

```text
Application -> Pod resolver -> kube-dns Service -> CoreDNS
                                                   |
                  cluster name: Kubernetes plugin --+
                  external name: upstream resolver -+
```

Normal ClusterIP Service records resolve to the Service IP. Headless Service records resolve to eligible endpoint addresses. ExternalName Services return a CNAME. DNS resolution alone does not establish that an application is reachable.

## Configuration and diagnostics

The `coredns` ConfigMap in `kube-system` usually contains a Corefile. Typical plugins include `kubernetes`, `forward`, `cache`, `health`, `ready`, and `reload`; the exact configuration depends on the cluster.

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl get service kube-dns -n kube-system
kubectl get configmap coredns -n kube-system -o yaml
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
kubectl exec curl-test-pod -- cat /etc/resolv.conf
kubectl exec curl-test-pod -- nslookup kubernetes.default.svc.cluster.local
```

Check Pod resolver settings, DNS Service endpoints, CoreDNS readiness/logs, and network policies. When DNS succeeds but HTTP fails, inspect the target Service selector, ready endpoints, target port, and application logs.

See the existing [resolver screenshot](../screenshots/08-resolv-conf.png), [DNS lookup screenshot](../screenshots/08-nslookup-fqdn.png), and [DNS troubleshooting lab](../../session-14-kubernetes-troubleshooting/09-service-dns-troubleshooting/README.md).
