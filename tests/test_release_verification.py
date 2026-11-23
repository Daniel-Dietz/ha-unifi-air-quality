"""Test the publisher's read-only release acceptance checks."""

from types import SimpleNamespace

import pytest

from dev import verify_release

REPO = "owner/repo"
TAG = "v1.2.3"
SHA = "a" * 40


@pytest.fixture
def release_state(monkeypatch):
    """Supply synthetic release and tag data without network access."""
    release = {
        "tag_name": TAG,
        "draft": False,
        "prerelease": False,
        "immutable": True,
    }
    ref = {"ref": f"refs/tags/{TAG}", "object": {"sha": SHA, "type": "commit"}}
    responses = {
        f"repos/{REPO}/releases/tags/{TAG}": release,
        f"repos/{REPO}/git/ref/tags/{TAG}": ref,
    }
    monkeypatch.setattr(verify_release, "api", responses.__getitem__)
    monkeypatch.setattr(verify_release.time, "sleep", lambda _: None)
    return release, ref


@pytest.mark.parametrize(
    ("field", "value"),
    [("immutable", False), ("immutable", None), ("draft", True),
     ("prerelease", True), ("tag_name", "v9.0.0")],
)
def test_invalid_release(release_state, monkeypatch, field, value):
    """Reject missing immutability or the wrong release before verifying."""
    release, _ = release_state
    release[field] = value

    def unexpected(*args, **kwargs):
        """Fail if attestation verification is attempted for invalid state."""
        pytest.fail("Invalid release reached attestation verification")

    monkeypatch.setattr(verify_release.subprocess, "run", unexpected)
    with pytest.raises(SystemExit, match="not a published immutable"):
        verify_release.verify_release(REPO, TAG, SHA)


@pytest.mark.parametrize("field", ["sha", "type"])
def test_wrong_tag_target(release_state, field):
    """Reject an unexpected commit or a different Git object type."""
    _, ref = release_state
    ref["object"][field] = "unexpected"
    with pytest.raises(SystemExit, match="does not point"):
        verify_release.verify_release(REPO, TAG, SHA)


@pytest.mark.parametrize(("codes", "succeeds"), [([0], True), ([1, 0], True),
                                                 ([1] * 6, False)])
def test_attestation(release_state, monkeypatch, codes, succeeds):
    """Require a successful signed attestation check with bounded retries."""
    calls = []
    results = iter(codes)

    def run(command, *, check, timeout):
        """Capture the exact read-only CLI invocation and simulate its exit code."""
        calls.append(command)
        assert check is False
        assert timeout == 30
        return SimpleNamespace(returncode=next(results))

    monkeypatch.setattr(verify_release.subprocess, "run", run)
    if succeeds:
        verify_release.verify_release(REPO, TAG, SHA)
    else:
        with pytest.raises(SystemExit, match="attestation verification failed"):
            verify_release.verify_release(REPO, TAG, SHA)
    assert calls == [["gh", "release", "verify", TAG, "--repo", REPO]] * len(codes)
