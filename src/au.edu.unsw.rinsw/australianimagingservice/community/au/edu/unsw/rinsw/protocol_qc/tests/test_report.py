import json

from australianimagingservice.community.au.edu.unsw.rinsw.protocol_qc.models import (
    ProtocolQcReport,
)
from australianimagingservice.community.au.edu.unsw.rinsw.protocol_qc.report import (
    write_report,
)


def test_write_report_serialises_template_path_and_status(tmp_path):
    report = ProtocolQcReport(
        protocol_qc_version="0.1.0-dev1",
        dictionary_version="1.1.2",
        template_path=tmp_path / "template.json",
        project_id="project",
        subject_id="subject",
        session_id="session",
        passed=True,
    )

    output_path = write_report(report, tmp_path / "nested" / "report.json")

    assert output_path.is_file()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["overall_status"] == "PASS"
    assert payload["template_path"] == str(tmp_path / "template.json")
