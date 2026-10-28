"""Verify downloaded research data against the versioned SHA-256 manifest."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "ARTIFACT_MANIFEST.json").read_text())
    failures = []
    for rel, expected in manifest["files_sha256"].items():
        path = root / rel
        if not path.is_file():
            failures.append(f"Missing: {rel}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(f"Changed: {rel}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Verified {len(manifest['files_sha256']):,} artifact files (SHA-256).")


if __name__ == "__main__":
    main()
