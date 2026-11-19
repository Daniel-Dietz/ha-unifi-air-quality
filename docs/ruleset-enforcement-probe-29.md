# Disposable ruleset enforcement probe for issue #29

This pull request must be closed without merging.

It verifies that the active main ruleset blocks failed required checks and
unresolved review conversations, then allows merging only after both are clear.
The intentionally failing test exists only on this disposable branch.
No production integration code is changed.
