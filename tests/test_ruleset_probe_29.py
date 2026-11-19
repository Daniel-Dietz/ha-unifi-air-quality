"""Intentional negative check for issue #29; never merge this disposable branch."""


def test_ruleset_rejects_failed_required_check() -> None:
    """Fail deliberately to verify the required-check merge gate."""
    raise AssertionError("Intentional issue #29 ruleset probe; never merge")
