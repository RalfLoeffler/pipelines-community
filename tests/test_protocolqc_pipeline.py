"""Repository-level checks for the canonical UNSW ProtocolQC pipeline."""

from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
SPEC = ROOT / "specs/australian-imaging-service-community-unsw/au/edu/unsw/rinsw/protocolqc.yaml"
SOURCE = (
    ROOT
    / "src/au.edu.unsw.rinsw/australianimagingservice/community/au/edu/unsw/rinsw"
    / "protocol_qc"
)


def test_protocolqc_spec_uses_unsw_source_entry_point():
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    assert spec["commands"]["protocol-qc"]["task"] == (
        "australianimagingservice.community.au.edu.unsw.rinsw.protocol_qc.workflow:protocol_qc_task"
    )
    assert "australianimagingservice-community-au-edu-unsw-rinsw" in spec["packages"]["pip"]
    assert "australianimagingservice" not in spec["packages"]["pip"]


def test_protocolqc_source_and_resource_are_canonical():
    assert (SOURCE / "workflow.py").is_file()
    assert (ROOT / "resources/protocol-qc-template/protocol-template.json").is_file()
    assert not (ROOT / "specs/ralfloeffler").exists()
