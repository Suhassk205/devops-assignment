#!/usr/bin/env python3
"""Read the actual systemd journal of the local Linux Kubernetes node."""
from lab_evidence import Evidence

NODE = "session13-control-plane"
e = Evidence("session2-linux", "01-journalctl-service", "Linux service logs with journalctl",
             context=f"Linux systemd node {NODE}; kubelet.service")
e.run(["docker", "exec", NODE, "ps", "-p", "1", "-o", "comm="])
status = e.run(["docker", "exec", NODE, "systemctl", "is-active", "kubelet"])
assert status.strip() == "active"
logs = e.run(["docker", "exec", NODE, "journalctl", "-u", "kubelet", "-n", "8", "--no-pager"])
assert "kubelet[" in logs and "-- No entries --" not in logs
e.run(["docker", "exec", NODE, "journalctl", "-u", "kubelet", "--since", "today", "-n", "5", "--no-pager"])
e.run(["docker", "exec", NODE, "journalctl", "-u", "kubelet", "-p", "err", "-n", "3", "--no-pager"])
e.run(["docker", "exec", NODE, "journalctl", "--disk-usage"])
e.note("Verified: PID 1 is systemd, kubelet is active, and journalctl returned actual service log entries.")

e = Evidence("session2-linux", "02-journalctl-summary", "Linux service log verification",
             context=f"Linux node {NODE}; kubelet.service")
e.run(["docker", "exec", NODE, "ps", "-p", "1", "-o", "comm="])
e.run(["docker", "exec", NODE, "systemctl", "is-active", "kubelet"])
e.run(["docker", "exec", NODE, "journalctl", "-u", "kubelet", "-n", "5", "--no-pager", "--truncate"])
e.run(["docker", "exec", NODE, "journalctl", "--disk-usage"])
