"""Validate the repository state required for a coordinated release."""

import argparse
import re
import subprocess
from pathlib import Path
from typing import Optional, Sequence


FINAL_SEMVER = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\Z")


class ReleasePreflightError(ValueError):
    """Raised when the checkout does not satisfy the release contract."""


def _validate_final_version(version: str) -> None:
    if not FINAL_SEMVER.fullmatch(version):
        raise ReleasePreflightError(
            f"VERSION.txt must contain a final SemVer version, not {version!r}"
        )


def read_version(version_file: Path) -> str:
    """Read the single-line canonical repository version."""
    contents = version_file.read_text(encoding="utf-8")
    version = contents.strip()
    if contents != f"{version}\n":
        raise ReleasePreflightError(
            "VERSION.txt must contain exactly one newline-terminated version"
        )
    return version


def validate_release(
    version: str,
    tag_name: str,
    tag_object_type: str,
    tag_target: str,
    head: str,
) -> str:
    """Validate final version, annotated tag, and tag target without Git I/O."""
    _validate_final_version(version)
    if tag_name != f"v{version}":
        raise ReleasePreflightError(
            f"release tag must be v{version}, not {tag_name!r}"
        )
    if tag_object_type != "tag":
        raise ReleasePreflightError(f"release tag {tag_name!r} must be annotated")
    if tag_target != head:
        raise ReleasePreflightError(
            f"release tag {tag_name!r} must resolve to HEAD ({head}), not {tag_target}"
        )
    return version


def _git(repository: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            check=True,
            cwd=repository,
            capture_output=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as error:
        raise ReleasePreflightError(
            error.stderr.strip() or "git release validation failed"
        ) from error
    return completed.stdout.strip()


def validate_repository_release(repository: Path, tag_name: str) -> str:
    """Validate a repository checkout against its canonical release version."""
    version = read_version(repository / "VERSION.txt")
    _validate_final_version(version)
    return validate_release(
        version,
        tag_name,
        _git(repository, "cat-file", "-t", tag_name),
        _git(repository, "rev-parse", f"{tag_name}^{{}}"),
        _git(repository, "rev-parse", "HEAD"),
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--tag", required=True)
    args = parser.parse_args(argv)

    try:
        print(validate_repository_release(args.repository, args.tag))
    except ReleasePreflightError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
