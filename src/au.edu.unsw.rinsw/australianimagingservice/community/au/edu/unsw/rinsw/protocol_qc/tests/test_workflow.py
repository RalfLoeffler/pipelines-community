import json
from types import SimpleNamespace

from australianimagingservice.community.au.edu.unsw.rinsw.protocol_qc import workflow


def test_protocol_qc_dry_run_reports_missing_template_sequence(tmp_path, monkeypatch, capsys):
    template_path = tmp_path / "template.json"
    template_path.write_text(
        json.dumps(
            {
                "Metadata": {"DictionaryVersion": "1.1.2", "SequenceList": ["T1"]},
                "T1": {"Default": {"Acquisition_Parameters": {}}},
            }
        ),
        encoding="utf-8",
    )
    row = SimpleNamespace(
        frameset=SimpleNamespace(id="project"),
        id="session",
        frequency_id=lambda frequency: "subject",
    )
    monkeypatch.setattr(workflow, "iter_source_dicom_series", lambda data_row: [])

    workflow.protocol_qc(row, protocol_template=str(template_path), dry_run=True)

    payload = json.loads(capsys.readouterr().out)
    assert payload["overall_status"] == "FAIL"
    assert payload["messages"] == ["Missing template sequences: T1"]
