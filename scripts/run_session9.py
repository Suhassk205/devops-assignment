#!/usr/bin/env python3
"""Execute Kubernetes Basics on an isolated namespace in the local cluster."""
import json
from lab_evidence import Evidence, raw_k

SESSION = "session9-k8s"
NS = "session9-homework"
APP = "kubernetes-basics"

def evidence(name, title):
    return Evidence(SESSION, name, title)

def ready(e, replicas):
    e.k(NS, "rollout", "status", f"deployment/{APP}", "--timeout=180s")
    state = json.loads(raw_k(NS, "get", "deployment", APP, "-o", "json"))
    assert state["status"].get("readyReplicas") == replicas
    e.k(NS, "get", "deployment,replicaset,pods", "-l", f"app={APP}")

e = evidence("05-tutorial-cluster", "Kubernetes Basics - cluster and namespace")
e.run(["kubectl", "--context", "kind-session13", "cluster-info"])
e.run(["kubectl", "--context", "kind-session13", "get", "nodes", "-o", "wide"])
e.k(NS, "create", "namespace", NS)

e = evidence("06-tutorial-deploy", "Kubernetes Basics - deploy an application")
e.k(NS, "create", "deployment", APP, "--image=nginx:1.27", "--port=80")
ready(e, 1)

e = evidence("07-tutorial-explore", "Kubernetes Basics - inspect Pods, logs, and containers")
pods = json.loads(raw_k(NS, "get", "pods", "-l", f"app={APP}", "-o", "json"))
pod = pods["items"][0]["metadata"]["name"]
e.k(NS, "describe", "pod", pod)
e.k(NS, "logs", pod, "--tail=8")
e.k(NS, "exec", pod, "--", "nginx", "-v")
e.k(NS, "exec", pod, "--", "printenv", "HOSTNAME")

e = evidence("08-tutorial-service", "Kubernetes Basics - expose and access the application")
e.k(NS, "expose", "deployment", APP, "--type=NodePort", "--port=80", "--target-port=80")
e.k(NS, "get", "service", APP)
e.k(NS, "get", "endpointslices", "-l", f"kubernetes.io/service-name={APP}")
body = e.k(NS, "exec", f"deployment/{APP}", "--", "curl", "--fail", "--silent", "--include", "--connect-timeout", "3", "--max-time", "10", "--retry", "10", "--retry-connrefused", "--retry-delay", "1", f"http://{APP}")
assert "200 OK" in body and "Welcome to nginx!" in body
nodeport = raw_k(NS, "get", "service", APP, "-o", "jsonpath={.spec.ports[0].nodePort}").strip()
body = e.run(["docker", "exec", "session13-control-plane", "curl", "--fail", "--silent", "--include", "--connect-timeout", "3", "--max-time", "10", "--retry", "10", "--retry-connrefused", "--retry-delay", "1", f"http://127.0.0.1:{nodeport}"])
assert "200 OK" in body

e = evidence("09-tutorial-scale-up", "Kubernetes Basics - scale from one to four replicas")
e.k(NS, "scale", f"deployment/{APP}", "--replicas=4")
ready(e, 4)
e.k(NS, "get", "endpointslices", "-l", f"kubernetes.io/service-name={APP}")

e = evidence("10-tutorial-scale-down", "Kubernetes Basics - scale down to two replicas")
e.k(NS, "scale", f"deployment/{APP}", "--replicas=2")
ready(e, 2)

e = evidence("11-tutorial-update", "Kubernetes Basics - rolling update to Nginx 1.28")
e.k(NS, "set", "image", f"deployment/{APP}", "nginx=nginx:1.28")
ready(e, 2)
version = e.k(NS, "exec", f"deployment/{APP}", "--", "nginx", "-v")
assert "nginx/1.28." in version
e.k(NS, "rollout", "history", f"deployment/{APP}")

e = evidence("12-tutorial-rollback", "Kubernetes Basics - roll back to Nginx 1.27")
e.k(NS, "rollout", "undo", f"deployment/{APP}", "--to-revision=1")
ready(e, 2)
version = e.k(NS, "exec", f"deployment/{APP}", "--", "nginx", "-v")
assert "nginx/1.27." in version
e.k(NS, "rollout", "history", f"deployment/{APP}")
body = e.k(NS, "exec", f"deployment/{APP}", "--", "curl", "--fail", "--silent", "--head", "--connect-timeout", "3", "--max-time", "10", "--retry", "10", "--retry-connrefused", "--retry-delay", "1", f"http://{APP}")
assert "200 OK" in body

e = evidence("13-tutorial-cleanup", "Kubernetes Basics - remove only the tutorial namespace")
e.k(NS, "delete", "namespace", NS, "--wait=true", "--timeout=120s")
e.run(["kubectl", "--context", "kind-session13", "get", "namespaces", "--field-selector", f"metadata.name={NS}"])
e.note("Verified: tutorial resources removed; other coursework namespaces were left in place.")
