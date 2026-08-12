import json

import pytest

from australianimagingservice.community.au.edu.unsw.rinsw.protocol_qc.protocol import (
    ProtocolTemplateError,
    load_protocol_template,
)


def test_load_protocol_template(tmp_path):
    template_path = tmp_path / "template.json"
    template_path.write_text(
        json.dumps(
            {"Metadata": {"DictionaryVersion": "1.1.2", "SequenceList": []}}
        ),
        encoding="utf-8",
    )
    assert load_protocol_template(template_path)["Metadata"]["DictionaryVersion"] == "1.1.2"


@pytest.mark.parametrize(
    "contents",
    ["{}", '{"Metadata": {"DictionaryVersion": ""}}'],
)
def test_invalid_protocol_template_is_rejected(tmp_path, contents):
    template_path = tmp_path / "template.json"
    template_path.write_text(contents, encoding="utf-8")
    with pytest.raises(ProtocolTemplateError):
        load_protocol_template(template_path)
