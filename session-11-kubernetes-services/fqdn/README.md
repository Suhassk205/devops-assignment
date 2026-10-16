# Kubernetes FQDN

A fully qualified domain name identifies a DNS name through its complete hierarchy.

For a Kubernetes Service, the usual form is:

```text
service.namespace.svc.cluster.local
```

For example, `yatri-backend-service.default.svc.cluster.local` identifies the Service in the `default` namespace. The cluster domain can be configured differently.

Pods in the same namespace can normally use `yatri-backend-service`. A Pod in another namespace can use `yatri-backend-service.default` or the complete name. Pod DNS search domains expand short names.

```bash
kubectl exec curl-test-pod -- cat /etc/resolv.conf
kubectl exec curl-test-pod -- nslookup yatri-backend-service.default.svc.cluster.local
kubectl exec curl-test-pod -- curl http://yatri-backend-service.default.svc.cluster.local
```

For a headless Service governing a StatefulSet, an individual Pod can have a stable name such as `web-stateful-0.web-service-headless.default.svc.cluster.local`.

See the existing [FQDN walkthrough](../fqdn.md), [headless Service exercise](../05-headless/README.md), and [saved DNS evidence](../screenshots/08-nslookup-fqdn.png).
