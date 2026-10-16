#!/usr/bin/env python3
"""Capture Terminal screenshots backed by actual saved command transcripts."""
from pathlib import Path
from capture_terminal import capture
import sys

root = Path(__file__).resolve().parents[1]
sessions = sys.argv[1:] or ["session-13-storage-hpa-probes", "session-15-helm", "session-17-devsecops"]
for session in sessions:
    for transcript in sorted((root / session / "evidence").glob("*.txt")):
        capture(transcript, root / session / "screenshots" / (transcript.stem + ".png"))
