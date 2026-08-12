"""XNAT/FrameTree-specific file access for ProtocolQC."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from fileformats.generic import File
from fileformats.medimage.dicom import DicomSeries
from frametree.core.row import DataRow


def iter_source_dicom_series(
    data_row: DataRow,
) -> Iterator[tuple[str, str | int | None, DicomSeries]]:
    """Yield original DICOM series available in an XNAT session row."""

    for (resource_path, order_key), entry in list(data_row.entries_dict.items()):
        if entry.datatype != DicomSeries or entry.is_derivative:
            continue
        yield resource_path, order_key, entry.item


def dicom_paths(series: DicomSeries) -> list[Path]:
    """Return local paths for a materialised FrameTree DICOM series."""

    return [Path(path) for path in series.contents]


def write_session_report(
    data_row: DataRow,
    report_path: Path,
    resource_path: str = "ProtocolQC@protocol-qc",
) -> None:
    """Upload a JSON report as a derived XNAT session entry.

    The exact resource label and overwrite behaviour require xnat4tests
    validation before production use.
    """

    existing_entries = {
        key[0]: entry for key, entry in list(data_row.entries_dict.items())
    }
    if resource_path in existing_entries:
        report_entry = existing_entries[resource_path]
    else:
        report_entry = data_row.create_entry(resource_path, datatype=File)

    report_entry.item = File(report_path)
