import pytest
from worker.services.security import verify_signature
from unittest.mock import patch

def test_verify_signature_success():
    with patch("worker.services.security.receiver.verify") as mock_verify:
        mock_verify.return_value = True
        verify_signature("body", "sig")
        mock_verify.assert_called_once()

def test_verify_signature_failure():
    with patch("worker.services.security.receiver.verify", side_effect=Exception("Invalid")):
        with pytest.raises(Exception):
            verify_signature("body", "sig")
