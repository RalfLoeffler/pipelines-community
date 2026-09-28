# Versioning policy

`VERSION.txt` is the only manually maintained coordinated-release version for
this repository. Its current development value is `0.1.0-dev.0`.

## Version source and changelog

The root version uses Semantic Versioning (`MAJOR.MINOR.PATCH`) with an
optional prerelease suffix. A development suffix, such as `-dev.0`, is not a
release and must not be tagged or published. Update `VERSION.txt` and the
Unreleased section of the root `CHANGELOG.md` together when preparing a
coordinated release.

## Release procedure

1. Replace the development value in `VERSION.txt` with the final SemVer release
   value and update `CHANGELOG.md`.
2. Commit those changes as the release commit.
3. Create an annotated tag named `v<final VERSION>` pointing to that release
   commit, then create the GitHub release from that tag.

The shared `scripts/release_preflight.py` validation reads `VERSION.txt` for
the coordinated container metapackage release. On GitHub release or tag-push
execution, it rejects a version unless it is final SemVer, the tag exactly
matches `v<VERSION>`, the tag is annotated, and the tag resolves to the
checked-out release commit.

CI does not publish snapshot container images. Branch, pull-request,
workflow-dispatch, and tag-push executions may test and build artifacts, but
container, PyPI, and documentation publication occur only for a GitHub release
after the shared preflight succeeds.

## Derived and component-specific versions

Package build metadata remains derived by Hatch VCS from repository tags; do
not add package version strings that duplicate `VERSION.txt`. The coordinated
release tag provides the VCS evidence used by Hatch VCS.

ProtocolQC versions, example specification versions, dependency versions,
schema versions, base-image tags, and protocol dictionary versions are
component-specific. They do not need to equal the root coordinated-release
version unless a later owner decision explicitly aligns them.
