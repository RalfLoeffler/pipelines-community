# ProtocolQC XNAT Pipeline

## Purpose

ProtocolQC compares DICOM acquisition parameters in an XNAT imaging session
against an approved protocol template stored as a JSON resource in the built
container image.

The design is based on the supplied Flywheel ProtocolQC gear, but separates the
platform-independent QC logic from XNAT/FrameTree access. Flywheel APIs,
Twilio notifications, Flywheel tags, and `/flywheel/v0/output` are not part of
this pipeline.

## Status

ProtocolQC is organized as the UNSW pipeline contribution. Its canonical
specification is `specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml`.
The source package is supplied by `src/au.edu.unsw.rinsw`; stage the complete
pipeline contribution together before release.

ProtocolQC is included in the UNSW package-test matrix and also has focused
pipeline validation in `.github/workflows/ci-cd.yml`. CI installs the UNSW
package with its test extra, runs its colocated pytest suite, builds its Python
distributions, and generates documentation from the canonical UNSW
specification. XNAT integration, the approved clinical template, and
DICOM/comparison parity remain production blockers.

## Layout

```text
src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/
    comparison.py   Parameter comparison logic
    dicom.py        DICOM reading and extraction
    models.py       Structured report models
    protocol.py     JSON template loading and validation
    report.py       JSON serialisation
    workflow.py     Pydra2App/XNAT entry point
    xnat_io.py      FrameTree/XNAT file access and report upload

resources/protocol-qc-template/
    protocol-template.json

specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/
    protocolqc.yaml

doc/protocol-qc/
    README.md       Usage, configuration, limitations, and acceptance criteria
```

## Scaffold map

| Path | Role |
| --- | --- |
| `src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/` | ProtocolQC implementation and colocated tests |
| `specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml` | Pydra2App container command definition |
| `resources/protocol-qc-template/` | Packaged JSON template resource |
| `requirements/quality-control/protocol-qc.txt` | Local external runtime requirements |
| `requirements/quality-control/protocol-qc-test.txt` | Focused test requirements |
| `doc/protocol-qc/README.md` | Pipeline documentation |

## Packaged protocol resource

The build command supplies `./resources` as the Pydra2App resources root. The
specification maps the resource directory named `protocol-qc-template` into the
container at:

```text
/opt/protocol-qc-template
```

The task receives this absolute path by default:

```text
/opt/protocol-qc-template/protocol-template.json
```

The implementation deliberately reads the JSON with `pathlib.Path` and does
not calculate a path relative to the Python package or repository. This is
important because the source repository's directory layout is not guaranteed
to exist inside a generated image.

Before building a release image, replace the example file at:

```text
resources/protocol-qc-template/protocol-template.json
```

with the approved template and validate its `Metadata.DictionaryVersion`.

## Configuration

The authoritative Pydra2App command definition is
`specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml`. Its defaults are:

| Parameter | Default | Meaning |
| --- | --- | --- |
| `ProtocolTemplate` | `/opt/protocol-qc-template/protocol-template.json` | Approved JSON template inside the image |
| `OutputResource` | `ProtocolQC@protocol-qc` | Session-level derived XNAT report path |
| `FailOnDeviation` | `false` | Raise after report generation when the result is FAIL |
| `DryRun` | `true` | Print the report without uploading it to XNAT |

The specification is authoritative for the container build. The separate
`requirements/quality-control/protocol-qc.txt` file lists external runtime
packages for local setup; the UNSW source package itself is supplied from this
repository during the pipeline build and is therefore not a third-party
dependency. Test tools are listed separately in
`requirements/quality-control/protocol-qc-test.txt`.

The specification lists the UNSW distribution name
`australianimagingservice-community-au-edu-unsw-rinsw` so Pydra2App includes
that local source package when invoked with `--source-package`; it is copied
from this repository rather than downloaded from PyPI.

When `FailOnDeviation=true`, the workflow writes or logs the report first and
then raises an error if the overall result is FAIL.

## XNAT-conform DICOM access

The pipeline receives a session-level `frametree.core.row.DataRow` from the
Pydra2App XNAT Container Service entry point.

`xnat_io.iter_source_dicom_series()` performs the XNAT access sequence:

1. Trigger FrameTree population through `data_row.entries_dict`.
2. Iterate all session entries.
3. Select entries whose datatype is `DicomSeries`.
4. Exclude derivative entries.
5. Access `entry.item`, which causes FrameTree/XNAT to materialise or download
   the resource into the container cache.
6. Read local paths through `DicomSeries.contents`.

The original XNAT files are treated as read-only. ProtocolQC does not modify
input DICOM files.

## XNAT-conform report output

The report is first written to a unique temporary directory. For a non-dry run,
`xnat_io.write_session_report()` creates or reuses a derived FrameTree entry and
assigns a `fileformats.generic.File` object to it. This lets the XNAT store
adapter upload the report rather than using the XNAT REST API directly.

Default derivative path:

```text
ProtocolQC@protocol-qc
```

The exact XNAT resource label and overwrite behaviour must be validated in the
local `xnat4tests` sandbox before production use.

## Current report fields

The current JSON report contains `protocol_qc_version`, `dictionary_version`,
`template_path`, `project_id`, `subject_id`, `session_id`, `overall_status`,
`sequences`, and `messages`. The report model is defined in
`src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/models.py` and the
workflow populates the session identifiers in
`src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/workflow.py`.

The report schema is still provisional. In particular, the current identifiers
and resolved template path must be reviewed against privacy and governance
requirements before production use.

## Build

From the `pipelines-community` repository root:

```powershell
pydra2app make xnat `
    .\specs\australian-imaging-service-community-unsw\au\edu\unsw\rinsw\protocolqc.yaml `
    --registry ghcr.io `
    --loglevel info `
    --resources-dir .\resources `
    --spec-root .\specs `
    --dont-check-registry `
    --source-package .\src\au.edu.unsw.rinsw
```

Expected image:

```text
ghcr.io/australian-imaging-service-community-unsw/au.edu.unsw.rinsw.protocolqc:0.1.0-dev1
```

On Windows, the installed Pydra2App version may generate backslashes in a
Dockerfile `COPY` path. Until fixed upstream, inspect and patch the generated
Dockerfile or build through WSL2.

## First sandbox launch

Use explicit safe values:

```text
DryRun = true
FailOnDeviation = false
OutputResource = ProtocolQC@protocol-qc
ProtocolTemplate = /opt/protocol-qc-template/protocol-template.json
```

## Tests

Tests are located under:

```text
src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/tests/
```

The intended test runner is pytest. From an environment containing the runtime
dependencies and pytest, run:

```powershell
python -m pytest src\au.edu.unsw.rinsw\australianimagingservice\community\au\edu\unsw\rinsw\protocol_qc\tests
```

The current suite covers comparison helpers, report serialisation, template
validation, and dry-run workflow behaviour. The XNAT test is deliberately
skipped until an `xnat4tests` fixture with synthetic DICOM is available. The
UNSW package's `test` extra provides pytest and coverage tooling; the runtime
requirements file is not a complete test environment definition.

## TODO: DICOM extraction parity

- Port enhanced-MR Shared Functional Groups extraction from the Flywheel gear.
- Port Siemens private-header extraction.
- Port Phoenix protocol parsing.
- Port phase-encoding polarity extraction from in-plane rotation.
- Port MR spectroscopy handling.
- Port calculated FOV, resolution, and slice-gap fields.
- Define behaviour for standard single-frame MR Image Storage.
- Replace broad exception handling with explicit tag and format checks.
- Add synthetic enhanced-MR, spectroscopy, and Phoenix fixtures.

## TODO: comparison parity

- Port Multi-Echo comparison.
- Port `Temporal_positions_multiplier` logic.
- Port `Echo_lines_multiplier` logic.
- Port expected DICOM file-count checks.
- Preserve the rule that any matching approved candidate means the sequence
  passes.
- Add schema validation for candidate protocols and acquisition parameters.
- Only `Acquisition_Parameters` are currently compared. `Sequence_Attributes`
  is loaded from the template but is not yet validated or included in results.

## TODO: sequence matching

- Current behavior uses an exact, case-sensitive `SeriesDescription` match.
- An acquired sequence absent from the template is recorded as failed.
- A template sequence absent from the session is added to the report messages
  and causes the overall result to fail.
- Overall PASS requires at least one acquired sequence, every acquired sequence
  to pass, and no missing template sequences.
- Confirm whether `SeriesDescription` remains the primary key.
- Add configurable normalisation for whitespace, case, and scanner suffixes.
- Decide whether `ProtocolName` is a fallback.
- Decide how duplicate sequence descriptions are represented.
- Define ordering and ordinal checks if the approved template requires them.
- Decide whether unexpected or missing sequences should remain failures or
  become warnings.

## TODO: XNAT integration

- Validate `DataRow.frequency_id("subject")` for the AIS medimage hierarchy.
- Validate that every original scan DICOM resource appears as a `DicomSeries`.
- Validate the report resource label generated by `ProtocolQC@protocol-qc`.
- Decide whether to overwrite, version, or reject an existing report.
- Decide whether PASS/FAIL should also be written to XNAT fields or assessor
  objects.
- Add an XNAT command-history-friendly summary to stdout.
- Add `xnat4tests` integration tests using synthetic DICOM only.
- Test sessions containing derived DICOM resources and confirm they are skipped.

## TODO: output and governance

- Finalise the JSON report schema and version it.
- Include source image version, Git commit, template checksum, and run timestamp.
- Resolve whether project, subject, and session identifiers may appear in the
  report and logs. The current report includes these identifiers, so the
  privacy acceptance criterion below is not yet satisfied.
- Define exit-code policy for QC deviations versus processing failures.
- Define notification handling outside the processing task.
- Document template approval, versioning, and release procedure.

## Initial acceptance criteria

- The packaged JSON template is readable at the configured container path.
- Original XNAT DICOM entries are discovered without modification.
- Each original DICOM series is represented in the session report.
- Numeric, numeric-list, and string-list comparisons are unit tested.
- `DryRun=true` produces a complete report in stdout and no XNAT write.
- `DryRun=false` uploads exactly one session-level JSON report.
- Privacy requirements for project, subject, and session identifiers are
  resolved and verified; the current implementation includes these identifiers
  in reports.
