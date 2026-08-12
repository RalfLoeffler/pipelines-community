"""Reserved for xnat4tests integration coverage with synthetic DICOM data."""

import pytest


@pytest.mark.skip(reason="Requires an xnat4tests fixture and synthetic DICOM data")
def test_xnat_integration_pending():
    """Document the deliberate boundary between unit and XNAT integration tests."""
