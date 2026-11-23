"""Verify a published immutable release without modifying GitHub state."""

import json
import subprocess
import sys
import time


def api(path: str) -> dict:
    """Read a GitHub API object using the authenticated CLI."""
    return json.loads(
        subprocess.check_output(["gh", "api", path], text=True)  # noqa: S603, S607
    )


def verify_release(repo: str, tag: str, sha: str) -> None:
    """Require the exact published tag, native immutability and signed attestation."""
    release = api(f"repos/{repo}/releases/tags/{tag}")
    if (
        release.get("tag_name") != tag
        or release.get("draft") is not False
        or release.get("prerelease") is not False
        or release.get("immutable") is not True
    ):
        raise SystemExit("Release is not a published immutable stable release")
    ref = api(f"repos/{repo}/git/ref/tags/{tag}")
    obj = ref.get("object", {})
    if (
        ref.get("ref") != f"refs/tags/{tag}"
        or obj.get("sha") != sha
        or obj.get("type") != "commit"
    ):
        # The publisher creates a lightweight tag; do not accept a different ref.
        raise SystemExit("Published tag does not point to the expected commit")

    for attempt in range(6):
        result = subprocess.run(  # noqa: S603
            ["gh", "release", "verify", tag, "--repo", repo],  # noqa: S607
            check=False,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"Verified immutable release {tag} at {sha}")
            return
        if attempt < 5:
            time.sleep(10)
    raise SystemExit("GitHub release attestation verification failed")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: verify_release.py REPO TAG COMMIT_SHA")
    verify_release(*sys.argv[1:])
