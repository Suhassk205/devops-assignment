#!/usr/bin/env python3
"""Run Session 13 exercises on the named local Kind cluster and save evidence.

Uses isolated session13-homework and session13-mini-homework namespaces.
Deletes only exercise pods, never data claims.
Run from the repository: python3 scripts/run_session13.py
"""
import json
import sys
from pathlib import Path
import subprocess
import time
from lab_evidence import CONTEXT, ROOT, Evidence, raw_k, wait_until

SESSION = "session-13-storage-hpa-probes"
BASE = ROOT / SESSION
NS = "session13-homework"
MINI_NS = "session13-mini-homework"
CPU_WORKERS = []


def apply(e, folder, files, ns=NS):
    for f in files:
        if folder == "mini-project":
            source = (BASE / folder / f).read_text()
            source = source.replace("namespace: production-webapp", "namespace: " + ns).replace("name: production-webapp", "name: " + ns)
            e.note("Applying " + str(BASE / folder / f) + " with isolated namespace " + ns)
            e.k(ns, "apply", "-f", "-", input=source)
        else:
            e.k(ns, "apply", "-f", str(BASE / folder / f))


def ready(e, pod, ns=NS):
    e.k(ns, "wait", "--for=condition=Ready", "pod/" + pod, "--timeout=120s")


def pod(ns, name):
    return json.loads(raw_k(ns, "get", "pod", name, "-o", "json"))


def is_ready(ns, name):
    return any(c["type"] == "Ready" and c["status"] == "True"
               for c in pod(ns, name)["status"].get("conditions", []))


def scaling(ns, deployment, minimum, e, load_name):
    started = time.monotonic()
    stressed = False
    while time.monotonic() - started < 240:
        dep = json.loads(raw_k(ns, "get", "deployment", deployment, "-o", "json"))
        if dep["spec"]["replicas"] > minimum and dep.get("status", {}).get("readyReplicas", 0) > minimum:
            return
        if time.monotonic() - started > 90 and not stressed:
            # Static Nginx requests may use too little CPU to cross the HPA target.
            # Add bounded CPU work inside the actual target containers, keeping
            # the declared 50% HPA threshold unchanged. Record it explicitly.
            e.note("HTTP traffic alone has not crossed the CPU threshold; adding 120 seconds of controlled CPU work inside target containers.")
            pods = json.loads(raw_k(ns, "get", "pods", "-l", "app=" + deployment, "-o", "json"))["items"]
            for p in pods:
                args = ["kubectl", "--context", CONTEXT, "-n", ns, "exec", p["metadata"]["name"], "--", "timeout", "120", "sh", "-c", "while :; do :; done"]
                e.note("$ " + __import__("shlex").join(args) + " [bounded background workload]")
                CPU_WORKERS.append(subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            stressed = True
        time.sleep(5)
    raise TimeoutError(f"HPA did not scale {deployment}; check recorded evidence")


START = sys.argv[1] if len(sys.argv) > 1 else "all"
if START not in {"all", "probes", "mini"}:
    raise SystemExit("Usage: run_session13.py [all|probes|mini]")

if START == "all":
    e = Evidence(SESSION, "00-environment", "Session 13 - local cluster prerequisites")
    e.run(["kubectl", "--context", CONTEXT, "get", "nodes"])
    e.run(["kubectl", "--context", CONTEXT, "get", "storageclass"])
    e.run(["kubectl", "--context", CONTEXT, "top", "nodes"])
    e.k(NS, "create", "namespace", NS, check=False)

    e = Evidence(SESSION, "01-emptydir", "emptyDir - data is lost when the Pod is recreated")
    apply(e, "01-volumes", ["emptydir-pod.yaml"])
    ready(e, "emptydir-demo")
    e.k(NS, "exec", "emptydir-demo", "--", "sh", "-c", 'echo "Suhas - emptyDir test" > /data/student.txt; cat /data/student.txt')
    e.k(NS, "delete", "pod", "emptydir-demo", "--wait=true")
    apply(e, "01-volumes", ["emptydir-pod.yaml"])
    ready(e, "emptydir-demo")
    e.k(NS, "exec", "emptydir-demo", "--", "sh", "-c", 'test ! -e /data/student.txt && echo "Verified: student.txt is absent after Pod recreation"')

    e = Evidence(SESSION, "02-hostpath", "hostPath - data survives Pod recreation on the same local node")
    apply(e, "01-volumes", ["hostpath-pod.yaml"])
    ready(e, "hostpath-demo")
    e.k(NS, "exec", "hostpath-demo", "--", "sh", "-c", 'echo "Suhas - hostPath test" > /data/student.txt; cat /data/student.txt')
    e.k(NS, "delete", "pod", "hostpath-demo", "--wait=true")
    apply(e, "01-volumes", ["hostpath-pod.yaml"])
    ready(e, "hostpath-demo")
    assert "Suhas" in e.k(NS, "exec", "hostpath-demo", "--", "cat", "/data/student.txt")

    e = Evidence(SESSION, "03-persistent-storage", "Static PV/PVC - data survives deletion of only the Pod")
    apply(e, "02-persistent-storage", ["pv.yaml", "pvc.yaml", "pod.yaml"])
    ready(e, "storage-demo")
    e.k(NS, "get", "pvc", "student-pvc")
    e.k(NS, "get", "pv", "session13-homework-pv")
    e.k(NS, "exec", "storage-demo", "--", "sh", "-c", 'echo "Suhas - persistent volume test" > /data/student.txt; cat /data/student.txt')
    e.k(NS, "delete", "pod", "storage-demo", "--wait=true")
    apply(e, "02-persistent-storage", ["pod.yaml"])
    ready(e, "storage-demo")
    assert "Suhas" in e.k(NS, "exec", "storage-demo", "--", "cat", "/data/student.txt")

    e = Evidence(SESSION, "04-dynamic-storage", "StorageClass - on-demand local PV provisioning")
    apply(e, "03-storageclass", ["sc.yaml", "pvc.yaml", "pod.yaml"])
    ready(e, "dynamic-storage-demo")
    e.k(NS, "get", "storageclass", "session13-local-path")
    e.k(NS, "get", "pvc", "dynamic-pvc", "-o", "wide")
    pv = raw_k(NS, "get", "pvc", "dynamic-pvc", "-o", "jsonpath={.spec.volumeName}").strip()
    e.k(NS, "get", "pv", pv)
    e.k(NS, "exec", "dynamic-storage-demo", "--", "sh", "-c", 'echo "Suhas - dynamically provisioned storage" > /data/student.txt; cat /data/student.txt')

    e = Evidence(SESSION, "05-hpa-baseline", "HPA - baseline before load")
    apply(e, "04-hpa", ["deployment.yaml", "service.yaml", "hpa.yaml"])
    e.k(NS, "rollout", "status", "deployment/hpa-demo", "--timeout=120s")
    wait_until(lambda: any("averageUtilization" in m.get("resource", {}).get("current", {})
                          for m in json.loads(raw_k(NS, "get", "hpa", "hpa-demo", "-o", "json")).get("status", {}).get("currentMetrics", [])), timeout=150)
    e.k(NS, "get", "hpa")
    e.k(NS, "get", "pods", "-l", "app=hpa-demo")
    e.k(NS, "top", "pods", "-l", "app=hpa-demo")
    e = Evidence(SESSION, "06-hpa-scaled", "HPA - real CPU load and observed scale-out")
    apply(e, "04-hpa", ["load-generator.yaml"])
    scaling(NS, "hpa-demo", 1, e, "homework-load-generator")
    e.k(NS, "get", "hpa")
    e.k(NS, "get", "pods", "-l", "app=hpa-demo")
    e.k(NS, "top", "pods", "-l", "app=hpa-demo")
    e.k(NS, "describe", "hpa", "hpa-demo")
    e.k(NS, "delete", "pod", "homework-load-generator", "--wait=false")


if START in {"all", "probes"}:
    e = Evidence(SESSION, "07-probes-healthy", "Startup, readiness and liveness probes - healthy baseline")
    apply(e, "05-probes", ["liveness.yaml", "readiness.yaml", "startup.yaml", "readiness-service.yaml"])
    e.k(NS, "exec", "readiness-demo", "--", "sh", "-c", 'if [ -f /usr/share/nginx/html/index.html.disabled ]; then mv /usr/share/nginx/html/index.html.disabled /usr/share/nginx/html/index.html; fi')
    for name in ["liveness-demo", "readiness-demo", "startup-demo"]:
        ready(e, name)
    e.k(NS, "get", "pods", "liveness-demo", "readiness-demo", "startup-demo")
    e.k(NS, "get", "endpointslice", "-l", "kubernetes.io/service-name=readiness-demo")

    e = Evidence(SESSION, "08-readiness-failure", "Readiness failure - Running but not Ready, no restart")
    e.k(NS, "exec", "readiness-demo", "--", "mv", "/usr/share/nginx/html/index.html", "/usr/share/nginx/html/index.html.disabled")
    wait_until(lambda: not is_ready(NS, "readiness-demo"), timeout=45, interval=2)
    e.k(NS, "get", "pod", "readiness-demo")
    e.k(NS, "get", "endpointslice", "-l", "kubernetes.io/service-name=readiness-demo", "-o", r'jsonpath={range .items[*].endpoints[*]}{.addresses} ready={.conditions.ready}{"\n"}{end}')
    e.k(NS, "get", "events", "--field-selector", "involvedObject.name=readiness-demo", "--sort-by=.lastTimestamp")
    e.k(NS, "exec", "readiness-demo", "--", "mv", "/usr/share/nginx/html/index.html.disabled", "/usr/share/nginx/html/index.html")
    ready(e, "readiness-demo")

    e = Evidence(SESSION, "09-liveness-restart", "Liveness failure - kubelet restarts the container")
    before = pod(NS, "liveness-demo")["status"]["containerStatuses"][0]["restartCount"]
    e.k(NS, "exec", "liveness-demo", "--", "mv", "/usr/share/nginx/html/index.html", "/usr/share/nginx/html/index.html.disabled")
    wait_until(lambda: pod(NS, "liveness-demo")["status"]["containerStatuses"][0]["restartCount"] > before, timeout=90, interval=2)
    ready(e, "liveness-demo")
    e.k(NS, "get", "pod", "liveness-demo")
    e.k(NS, "get", "events", "--field-selector", "involvedObject.name=liveness-demo", "--sort-by=.lastTimestamp")
    e.k(NS, "get", "pods", "liveness-demo", "readiness-demo", "startup-demo")


e = Evidence(SESSION, "10-mini-project", "Mini-project - deployment, persistent data, probes and Service")
apply(e, "mini-project", ["namespace.yaml", "pvc.yaml", "deployment.yaml", "service.yaml", "hpa.yaml"], ns=MINI_NS)
e.k(MINI_NS, "rollout", "status", "deployment/web-app", "--timeout=120s")
old = json.loads(raw_k(MINI_NS, "get", "pods", "-l", "app=web-app", "-o", "json"))["items"][0]["metadata"]["name"]
e.k(MINI_NS, "exec", old, "--", "sh", "-c", 'echo "Suhas - mini-project persistent data" > /data/homework.txt; cat /data/homework.txt')
e.k(MINI_NS, "delete", "pod", old, "--wait=true")
e.k(MINI_NS, "rollout", "status", "deployment/web-app", "--timeout=120s")
new = json.loads(raw_k(MINI_NS, "get", "pods", "-l", "app=web-app", "-o", "json"))["items"][0]["metadata"]["name"]
assert "Suhas" in e.k(MINI_NS, "exec", new, "--", "cat", "/data/homework.txt")
e.k(MINI_NS, "get", "pods", "-l", "app=web-app")
e.k(MINI_NS, "get", "pvc", "web-data")
e.k(MINI_NS, "get", "svc", "web-service")
e.k(MINI_NS, "exec", new, "--", "curl", "--fail", "--retry", "10", "--retry-connrefused", "--retry-delay", "1", "-sI", "http://web-service")

e = Evidence(SESSION, "11-mini-project-scaled", "Mini-project - autoscaling under controlled CPU load")
e.k(MINI_NS, "get", "hpa", "web-app-hpa")
for p in json.loads(raw_k(MINI_NS, "get", "pods", "-l", "app=web-app", "-o", "json"))["items"]:
    args = ["kubectl", "--context", CONTEXT, "-n", MINI_NS, "exec", p["metadata"]["name"], "--", "timeout", "120", "sh", "-c", "while :; do :; done"]
    e.note("$ " + __import__("shlex").join(args) + " [bounded background workload]")
    CPU_WORKERS.append(subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
scaling(MINI_NS, "web-app", 2, e, "")
e.k(MINI_NS, "get", "hpa", "web-app-hpa")
e.k(MINI_NS, "get", "pods", "-l", "app=web-app")
e.k(MINI_NS, "top", "pods", "-l", "app=web-app")
e.k(MINI_NS, "describe", "hpa", "web-app-hpa")
for worker in CPU_WORKERS:
    worker.terminate()
print("Session 13 verification complete. CPU work expires automatically; HTTP load pod removed.", flush=True)
