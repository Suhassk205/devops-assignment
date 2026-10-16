#!/usr/bin/env python3
"""Print a small resource inventory from saved local Terraform state files."""
import json
from pathlib import Path
import sys

for name in sys.argv[1:]:
    path = Path(name)
    data = json.loads(path.read_text())
    resources = [r for r in data.get("resources", []) if r.get("mode") == "managed"]
    print(f"{path.name}: {len(resources)} managed resource(s)")
    for resource in resources:
        for instance in resource.get("instances", []):
            attributes = instance.get("attributes", {})
            print(f"  {resource['type']}.{resource['name']}")
            for key in ["id", "bucket", "region"]:
                if attributes.get(key) is not None:
                    print(f"    {key}: {attributes[key]}")
