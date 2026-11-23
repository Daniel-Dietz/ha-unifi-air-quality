# Release integrity and acceptance

## Existing v0.6.1

On 2026-11-23 the repository administrator confirmed enabling **Settings →
General → Releases → Enable release immutability**. GitHub applies the setting
only to releases published afterward; it does not convert existing releases.
The administrator can independently read the setting with an appropriately
authorized GitHub CLI:

```bash
gh api repos/Daniel-Dietz/ha-unifi-air-quality/immutable-releases
```

Expect `enabled: true`. This endpoint requires administration read access;
the publisher must not receive administration credentials to query it.

The [live legacy tag ruleset](https://github.com/Daniel-Dietz/ha-unifi-air-quality/rules/27943474)
was read back on 2026-11-23: active, target `tag`, include exactly
`refs/tags/v0.6.1`, no exclusions, no bypass actors, and rules `deletion`,
`non_fast_forward` and `update` (no fetch-and-merge exception). It does not
restrict new version tag creation. The current main ruleset remains active.
The importable [legacy ruleset template](../.github/rulesets/legacy-release-tags.json)
records the configuration; committing it does not change GitHub settings.

The existing published v0.6.1 tag points to
`d3de6c7931d7fbbcc7cb5c4214a67f6ce7860971` (PR #45's merge commit).
Its release API returns `immutable: false`, `draft: false` and
`prerelease: false`. Do not assert native release immutability or a native
release attestation for this version. Never delete, replace, republish or
retarget it. Verify the ruleset and tag SHA through read-only API calls,
not attempted destructive changes. Retain the pinned commit and package for
[recovery](install-upgrade-rollback.md).

## Publish a subsequent version

1. Before approving a version bump, confirm the live main and legacy rulesets
   and native release immutability setting. Keep the bypass lists empty.
2. Update the manifest, Python project version and changelog together through a
   reviewed PR. Require Tests, Security, HACS and Hassfest and the final Codex
   review as described in the [maintainer guide](maintainer-ruleset.md).
3. The [publisher](../.github/workflows/release.yml) runs on manifest changes
   on protected main or manual dispatch from main. A workflow-only change
   must not trigger a release. The publisher requires all four validations
   on the same current main SHA and refuses existing mismatched or orphaned
   tags. It never modifies a published release or reuses its name.
4. After creation, or on a same-commit retry, the publisher verifies the
   published release state, exact tag SHA, native immutability and GitHub's
   signed release attestation. A missing or invalid attestation or
   `immutable: false` fails the job. This is a post-publication check, not a
   guarantee that a release could not be created with settings disabled.
   Check the admin setting before publication; do not add an admin token to CI.
5. Record the release URL, tag SHA, successful publisher job and attestation
   verification for the first real subsequent release in #46. Do not publish
   an artificial version solely to produce acceptance evidence.

Read-only manual verification of a new published release, from an authenticated
GitHub CLI (substitute the actual version and accepted main commit):

```bash
python dev/verify_release.py Daniel-Dietz/ha-unifi-air-quality VERSION_TAG COMMIT_SHA
```

The script checks the release and tag via GitHub API and runs
`gh release verify` with bounded retries for attestation availability.
It makes no writes. A successful run is evidence for that release only.

## Failed publication or verification

Keep the release unaccepted if the publisher fails. Inspect the failed step
and the actual GitHub state. Correct settings or transient attestation
availability, then verify again without touching the published tag.
If a release was already published without native immutability, enabling the
setting afterward cannot repair that release; preserve its identity, record
the incident and review explicit tag protection and the next legitimate version.
Do not delete a release, move a tag, weaken the ruleset or bypass CI to obtain
a green run.

References: [GitHub release immutability](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases),
[repository settings](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes),
[CLI attestation verification](https://cli.github.com/manual/gh_release_verify).
