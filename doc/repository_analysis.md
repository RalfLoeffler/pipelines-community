# Repository Analysis: pipelines-community

**Branch reviewed:** `local-qwen-task`
**Commit baseline:** `d4b9a82` (`added scaffold files`)

## Scope and status

This document describes the committed `local-qwen-task` baseline and the UNSW
ProtocolQC pipeline contribution being staged alongside it.

For scaffold-specific behavior, configuration, and limitations, see the
[ProtocolQC scaffold README](protocol-qc/README.md).

## Repository layout

The committed repository contains a Sydney Imaging package area and an UNSW
package/specification area:

- Sydney Imaging package: `src/au.edu.sydney.sydneyimaging/`
- UNSW RINSW package metadata and specifications: `src/au.edu.unsw.rinsw/` and
  `specs/australian-imaging-service-community-unsw/`
- Pipeline specifications: `specs/australian-imaging-service-community/` and
  `specs/australian-imaging-service-community-unsw/`
- Root-level tests: `tests/`
- Maintained documentation: `doc/`
- Generated documentation output: `docs/`

The singular `doc/` directory is the canonical location for maintained
documentation. The plural `docs/` directory is intentionally ignored by
`.gitignore` and is used for generated documentation artifacts.

## Package entry points and build configuration

The Sydney Imaging package exposes the `t1_preproc` workflow from
`src/au.edu.sydney.sydneyimaging/australianimagingservice/community/au/edu/sydney/sydneyimaging/t1_preproc.py`.
Its build, dependency, test, Black, Flake8, and Codespell configuration is in
`src/au.edu.sydney.sydneyimaging/pyproject.toml`.

The UNSW area has its own build and development configuration in
`src/au.edu.unsw.rinsw/pyproject.toml`, with ProtocolQC source under that
package and its canonical specification under
`specs/australian-imaging-service-community-unsw/`. Pipeline specifications
define Pydra2App commands and metadata under `specs/`.

## Dependency management

The root CI/bootstrap dependency is declared in `requirements.txt`.
Package-specific runtime and development dependencies are declared in each
package's `pyproject.toml`. ProtocolQC also has separate runtime and test
requirements in `requirements/quality-control/` and container dependencies in
the canonical UNSW specification.

The ProtocolQC task is supplied by the UNSW source package, so the specification
does not declare a third-party `australianimagingservice` dependency. Runtime
requirements are in `requirements/quality-control/protocol-qc.txt`; pytest and
pytest-cov are in `protocol-qc-test.txt`.

## Tests and CI

The repository's CI workflow is `.github/workflows/ci-cd.yml`. It installs the
root requirements, generates documentation, tests the Sydney Imaging package
with pytest and coverage, builds distributions, and builds pipeline
containers. The UNSW matrix entry runs the ProtocolQC colocated unit tests and
builds its distributions; the dedicated ProtocolQC job compiles the source and
validates the canonical UNSW specification/resource build.

The committed package test extras include pytest and pytest-cov in
`src/au.edu.sydney.sydneyimaging/pyproject.toml` and
`src/au.edu.unsw.rinsw/pyproject.toml`. Coverage policy is recorded in
`codecov.yml`; the repository-level `.coveragerc` supplies the shared coverage
configuration used by CI.

Root tests are under `tests/`, including documentation generation and a
historically named Pydra2App container-command integration test:
`tests/test_docs.py`, `tests/test_protocolqc.py`, and the other pipeline test
modules. `tests/test_protocolqc.py` does not exercise the local working-tree
ProtocolQC implementation. ProtocolQC unit tests are under
`src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/tests/`;
the UNSW matrix and dedicated ProtocolQC job run them, while live XNAT
integration remains deferred.

### CI visibility

| Area | Committed baseline | Package-test job in CI |
| --- | --- | --- |
| Sydney Imaging | Yes: `src/au.edu.sydney.sydneyimaging/` | Yes |
| UNSW package/specification area | Yes: `src/au.edu.unsw.rinsw/` and `specs/australian-imaging-service-community-unsw/` | Yes |
| UNSW ProtocolQC pipeline | Yes: UNSW package and canonical spec | UNSW matrix plus dedicated job |

## Formatting, linting, and typing

Black, Flake8, and Codespell are configured for the committed package areas in
their respective `pyproject.toml` files. Pre-commit is listed as a development
dependency, but no repository-level `.pre-commit-config.yaml` is present.

No mypy, Pyright, or equivalent type-checking configuration is present. The
ProtocolQC source uses annotations and is covered by the UNSW package's test
extra, but no type checker is configured.

## Documentation generation

CI deliberately keeps generated documentation under `docs/`:

- `pydra2app make-docs` writes generated pipeline documentation to
  `docs/pipelines`: `.github/workflows/ci-cd.yml`
- The generated HTML is staged under `docs/build/html` before deployment:
  `.github/workflows/ci-cd.yml`

These generated paths must not be renamed to `doc/`. Authored ProtocolQC
documentation belongs under `doc/protocol-qc/README.md`.

## UNSW ProtocolQC pipeline

The UNSW ProtocolQC pipeline consists of:

- Implementation: `src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/`
- Specification: `specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml`
- Resource: `resources/protocol-qc-template/protocol-template.json`
- Requirements: `requirements/quality-control/protocol-qc.txt`
- Documentation: `doc/protocol-qc/README.md`

Stage these paths as one coherent pipeline contribution. The approved clinical
template content, live XNAT integration, and DICOM/comparison parity remain
production blockers documented in the ProtocolQC README.

## Risks and follow-up

- The generated-documentation workflow and authored-documentation convention
  must remain separate: `.github/workflows/ci-cd.yml`, `.gitignore`.
- ProtocolQC has a dedicated CI job, but its XNAT integration test remains
  deferred: `src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/tests/test_xnat_io.py`.
- Root tests and documentation generation depend on external Pydra2App tooling:
  `tests/test_docs.py`, `.github/workflows/ci-cd.yml`.
- ProtocolQC still needs an `xnat4tests` integration suite and an approved
  clinical protocol template before production deployment.
