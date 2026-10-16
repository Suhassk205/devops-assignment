#!/usr/bin/env python3
"""Install pinned official scanner releases, verifying their SHA-256 checksums."""
import hashlib
import io
from pathlib import Path
import platform
import tarfile
import time
import urllib.request

target = Path(__file__).resolve().parents[1] / ".tools" / "bin"
target.mkdir(parents=True, exist_ok=True)
system = platform.system()
arch = platform.machine().lower()
arm = arch in {"arm64", "aarch64"}
if system not in {"Darwin", "Linux"}:
    raise SystemExit("This installer supports macOS and Linux")


def download(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


for repo, version, asset in [
    ("aquasecurity/trivy", "0.76.0", f"trivy_0.76.0_{'macOS' if system == 'Darwin' else 'Linux'}-{'ARM64' if arm else '64bit'}.tar.gz"),
    ("gitleaks/gitleaks", "8.30.1", f"gitleaks_8.30.1_{'darwin' if system == 'Darwin' else 'linux'}_{'arm64' if arm else 'x64'}.tar.gz"),
]:
    tool = repo.split("/")[-1]
    base = f"https://github.com/{repo}/releases/download/v{version}/"
    checksums = download(base + f"{tool}_{version}_checksums.txt").decode()
    expected = next(line.split()[0] for line in checksums.splitlines() if line.split()[-1].lstrip("*") == asset)
    archive = download(base + asset)
    if hashlib.sha256(archive).hexdigest() != expected:
        raise SystemExit(f"Checksum mismatch: {asset}")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        entry = next(m for m in package.getmembers() if m.isfile() and Path(m.name).name == tool)
        (target / tool).write_bytes(package.extractfile(entry).read())
    (target / tool).chmod(0o755)
    print(f"Installed {tool} {version}; SHA-256 verified", flush=True)
