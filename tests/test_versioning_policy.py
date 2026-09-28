"""Repository-level checks for the coordinated-release versioning contract."""

import re
from pathlib import Path

from scripts.release_preflight import ReleasePreflightError, validate_release


ROOT = Path(__file__).parents[1]
VERSION = ROOT / "VERSION.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
POLICY = ROOT / "doc/versioning.md"
CI_WORKFLOW = ROOT / ".github/workflows/ci-cd.yml"
RELEASE_GATE = (
    "github.event_name == 'release' && "
    "needs.release-preflight.outputs.validated == 'true'"
)
SEMVER_IDENTIFIER = r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
STRICT_VERSION_SEMVER = re.compile(
    rf"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    rf"(?:-{SEMVER_IDENTIFIER}(?:\.{SEMVER_IDENTIFIER})*)?\Z"
)


def _workflow_step(workflow: str, name: str) -> str:
    marker = f"    - name: {name}\n"
    start = workflow.index(marker)
    end = workflow.find("\n    - ", start + len(marker))
    return workflow[start:] if end == -1 else workflow[start:end]


def test_root_version_is_a_strict_semver_value():
    contents = VERSION.read_text(encoding="utf-8")
    version = contents.strip()

    assert contents == f"{version}\n"
    assert STRICT_VERSION_SEMVER.fullmatch(version)


def test_root_version_rejects_invalid_semver_values():
    invalid_versions = (
        "1.2",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "1.2.3-",
        "1.2.3-dev..0",
        "1.2.3-01",
        "1.2.3+build",
    )

    for version in invalid_versions:
        assert not STRICT_VERSION_SEMVER.fullmatch(version)


def test_policy_documents_the_canonical_version_and_component_independence():
    policy = POLICY.read_text(encoding="utf-8")

    assert (
        "`VERSION.txt` is the only manually maintained coordinated-release version"
        in policy
    )
    assert "Package build metadata remains derived by Hatch VCS" in policy
    assert (
        "ProtocolQC versions, example specification versions, dependency versions,"
        in policy
    )
    assert "do not need to equal the root coordinated-release" in policy


def test_changelog_has_an_unreleased_section():
    changelog = CHANGELOG.read_text(encoding="utf-8")

    assert changelog.startswith("# Changelog\n")
    assert "## [Unreleased]" in changelog


def test_preflight_accepts_a_matching_annotated_final_release_tag():
    assert (
        validate_release("1.2.3", "v1.2.3", "tag", "release-commit", "release-commit")
        == "1.2.3"
    )


def test_preflight_rejects_a_mismatched_tag():
    try:
        validate_release(
            "1.2.3", "v1.2.4", "tag", "release-commit", "release-commit"
        )
    except ReleasePreflightError as error:
        assert "must be v1.2.3" in str(error)
    else:
        raise AssertionError("mismatched tag was accepted")


def test_preflight_rejects_a_tag_that_does_not_target_head():
    try:
        validate_release("1.2.3", "v1.2.3", "tag", "tag-commit", "head-commit")
    except ReleasePreflightError as error:
        assert "must resolve to HEAD" in str(error)
    else:
        raise AssertionError("tag with a different target was accepted")


def test_preflight_rejects_a_lightweight_tag():
    try:
        validate_release(
            "1.2.3", "v1.2.3", "commit", "release-commit", "release-commit"
        )
    except ReleasePreflightError as error:
        assert "must be annotated" in str(error)
    else:
        raise AssertionError("lightweight tag was accepted")


def test_preflight_rejects_prerelease_and_malformed_versions():
    for version in ("1.2.3-dev.0", "01.2.3", "1.2", "v1.2.3"):
        try:
            validate_release(
                version, f"v{version}", "tag", "release-commit", "release-commit"
            )
        except ReleasePreflightError as error:
            assert "final SemVer" in str(error)
        else:
            raise AssertionError(f"non-final version {version!r} was accepted")


def test_ci_collects_preflight_tests_and_gates_publications():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "release-preflight:" in workflow
    assert 'python3 scripts/release_preflight.py --tag "$RELEASE_TAG"' in workflow
    assert "tests/test_versioning_policy.py" in workflow
    assert "needs: [build-docs, release-preflight]" in workflow
    assert "needs: [python, release-preflight]" in workflow
    assert "needs: [build-docs, pipelines, release-preflight]" in workflow
    assert workflow.count(f"if: {RELEASE_GATE}") == 4

    pypi_eligibility = _workflow_step(workflow, "Check for PyPI token on tag")
    pypi_upload = _workflow_step(workflow, "Upload to PyPI")
    pypi_mirror = _workflow_step(workflow, "Wait for package to mirror")
    assert f"if: {RELEASE_GATE}" in pypi_eligibility
    assert "if: steps.deployable.outputs.DEPLOY" in pypi_upload
    assert "if: steps.deployable.outputs.DEPLOY" in pypi_mirror

    assert f"- uses: docker/login-action@v2\n      if: {RELEASE_GATE}" in workflow
    container_publish = _workflow_step(workflow, "Build and push container images")
    assert f"if: {RELEASE_GATE}" in container_publish

    docs_eligibility = _workflow_step(
        workflow, "Check for GHPAGES_DEPLOY_KEY token on tag"
    )
    docs_publish = _workflow_step(workflow, "Deploy docs")
    docs_dispatch = _workflow_step(workflow, "Trigger rebuild of docs")
    assert f"if: {RELEASE_GATE}" in docs_eligibility
    assert "if: steps.deployable.outputs.DEPLOY" in docs_publish
    assert "if: steps.deployable.outputs.DEPLOY" in docs_dispatch
    assert "git describe --tags --abbrev=0" not in workflow
