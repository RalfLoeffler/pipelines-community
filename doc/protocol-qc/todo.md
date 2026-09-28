# ProtocolQC Flywheel-to-XNAT port TODO

## Scope and source of truth

- Completed work belongs in `CHANGELOG.md` and is removed from this active
  TODO list; keep this document limited to outstanding work.
- [ ] Preserve the XNAT design already established in this repository: a
  session-level Pydra2App command, a consolidated JSON report, and FrameTree
  read/write access.
- [ ] Treat the existing XNAT scaffold as the target implementation:
  `src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw/protocol_qc/`,
  with the canonical command specification at
  `specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml`.

## 1. Agree the production contract

- [ ] Define the parity boundary: which Flywheel QC behaviours are mandatory in
  XNAT and which are intentionally platform-specific exclusions.
- [ ] Approve the session report schema and version it. Decide whether project,
  subject, and session identifiers may appear in report payloads and stdout.
- [ ] Define the required report provenance: source image version, Git commit,
  template checksum, and run timestamp.
- [ ] Define the exit-code policy for a QC deviation, invalid input, unreadable
  DICOM, and an XNAT upload failure.
- [ ] Decide how an existing `ProtocolQC@protocol-qc` derived resource is
  handled: overwrite, version, or reject.
- [ ] Decide whether PASS/FAIL is represented only in the JSON report or is
  also written to XNAT fields or assessor objects.
- [ ] Confirm sequence-matching semantics: `SeriesDescription` normalization,
  optional `ProtocolName` fallback, duplicate series, missing expected
  sequences, and unexpected acquired sequences.
- [ ] Define the governed template workflow: approval owner, version,
  checksum, release process, and whether templates remain image-packaged or
  become a controlled XNAT project resource.
- [ ] Provide and test a supported facility to create a protocol-template JSON
  file from an approved, de-identified reference acquisition or XNAT session.
  Define its inputs, generated schema, validation, provenance, and approval
  handoff before making it available to users.

## 2. Prepare safe parity fixtures

- [ ] Build compact synthetic, de-identified DICOM fixtures in tests; do not
  copy the legacy clinical sample DICOM files into this repository.
- [ ] Obtain approval-gated, de-identified template extracts that cover
  multiple candidates, multi-echo scans, and file-count rules. Candidate
  references include the source gear's BASR, CHeBA VCI, and MND dictionaries.
- [ ] Create golden normalized results from reviewed Flywheel outputs, including
  the multi-echo/file-count example, rather than treating the legacy
  `test_run.py` as an executable oracle (it is stale).
- [ ] Cover enhanced MR, standard MR, MR spectroscopy, Siemens private headers,
  Phoenix reports, derived images, corrupt/missing tags, empty series, and
  duplicate sequence descriptions.

## 3. Complete platform-independent DICOM extraction

- [ ] Port enhanced-MR Shared Functional Groups extraction into
  `protocol_qc/dicom.py`.
- [ ] Port calculated FOV, resolution, slice gap, temporal positions, and
  multi-echo values with explicit DICOM-tag and format handling.
- [ ] Port Siemens private-header extraction, Phoenix protocol parsing, and
  phase-encoding polarity derivation where approved fixtures demonstrate the
  expected behaviour.
- [ ] Implement and test MR spectroscopy handling.
- [ ] Specify handling of single-frame MR Image Storage rather than relying on
  the legacy gear's abort behaviour.
- [ ] Replace broad DICOM-read exception handling with specific, actionable
  errors once the fixture coverage defines expected failure modes.

## 4. Complete comparison and template parity

- [ ] Keep the existing rule that a sequence passes if any approved candidate
  passes.
- [ ] Validate `Sequence_Attributes`, including `Multi-Echo`,
  `Temporal_positions_multiplier`, `Echo_lines_multiplier`, and expected
  DICOM file counts.
- [ ] Enforce dictionary-version compatibility when extraction supplies a
  dictionary version, in addition to the current minimal template validation.
- [ ] Define and test the intentional string-list rule. The XNAT scaffold
  preserves multiplicity, while the legacy Flywheel implementation compares
  sets.
- [ ] Add schema validation for candidate protocols and acquisition-parameter
  definitions, including absent values, `NA`, numeric tolerances, and lists.
- [ ] Compare normalized XNAT results against the approved golden corpus for
  all supported dictionary features.

## 5. Validate XNAT and container integration

- [ ] Add `xnat4tests` coverage with a synthetic session to verify discovery of
  original `DicomSeries` entries and exclusion of derivative entries.
- [ ] Verify the AIS medimage hierarchy, including
  `DataRow.frequency_id("subject")`, project/session identifiers, and source
  file immutability.
- [ ] Verify `DryRun=true` emits a complete report without an XNAT write.
- [ ] Verify `DryRun=false` writes exactly one session report to
  `ProtocolQC@protocol-qc` and exercise the agreed existing-resource policy.
- [ ] Verify that a report is emitted before `FailOnDeviation=true` raises for
  an overall failed result.
- [ ] Add an XNAT command-history-friendly summary to stdout.
- [ ] Build the canonical Pydra2App specification and launch it in an XNAT
  sandbox. Confirm resource mounting at
  `/opt/protocol-qc-template/protocol-template.json`, parameter mapping,
  stdout summary, report visibility, and command-history behaviour.

## 6. Deferred platform integrations

- [ ] Define deferred platform behaviour for SMS messaging, session tagging,
  and per-acquisition QC output files: triggers, destinations, permissions,
  retention, failure handling, privacy, and the XNAT equivalents (if any).
- [ ] Implement these integrations only after their requirements, privacy
  posture, XNAT data model, and operational ownership are approved.

## 7. Release readiness

- [ ] Replace `resources/protocol-qc-template/protocol-template.json` only
  after an approved production template is available.
- [ ] Replace the proof-of-principle XNAT/Docker scaffold with validated
  ProtocolQC content before representing the pipeline as functionally
  implemented or production-ready.
- [ ] Run the focused ProtocolQC suite, the CI-equivalent coverage/spec checks,
  the broader UNSW package matrix, and the generated-container build.
- [ ] Validate a controlled, de-identified, production-like XNAT session across
  supported scanners/vendors and confirm service-account permissions.
- [ ] Update `doc/protocol-qc/README.md` with the final behaviour, supported
  DICOM classes, template governance, operational runbook, and remaining
  limitations.

## Completion criteria

- [ ] The XNAT pipeline has documented, tested parity for every included
  Flywheel QC rule and explicit exclusions for platform-specific behaviour.
- [ ] The report schema, privacy posture, template governance, resource
  lifecycle, and exit-code policy have approval.
- [ ] Synthetic unit, XNAT sandbox, container-service, and controlled
  production-like validation have passed.
