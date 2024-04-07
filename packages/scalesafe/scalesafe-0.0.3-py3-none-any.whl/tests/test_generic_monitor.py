import pytest
from unittest.mock import patch
from scalesafe.generic import GenericMonitor
from scalesafe.exceptions import ScaleSafeTokenError, ResourceNotFoundError
import os

# Fixture for creating a GenericMonitor instance
@pytest.fixture
def monitor():
    return GenericMonitor()

@pytest.fixture
def get_api_key():
    return os.environ.get('SCALESAFE_API_KEY_TEST')

# Test exceptions related to the API key retrieval
def test_get_api_key_exception(monitor):
    os.environ['SCALESAFE_API_KEY'] = ""
    with patch.dict(os.environ, {'SCALESAFE_API_KEY': ''}):
        with pytest.raises(ScaleSafeTokenError):
            monitor._get_api_key()

# Test exceptions when monitoring with a wrong API key
def test_monitor_with_wrong_api_key(monitor):
    with pytest.raises(ScaleSafeTokenError):
        monitor.monitor(data={'data': 'temp'}, api_key='wrong_key')

# Test exceptions when monitoring with a non-existent API key in environment
def test_monitor_with_valid_api_key(monitor):
    with pytest.raises(ResourceNotFoundError):
        monitor.monitor(data={'data': 'temp'}, api_key=os.environ.get('SCALESAFE_API_KEY_TEST'))

# Test API key workflow when passed through constructor
def test_api_key_from_constructor():
    api_key_constructor = 'test_api_key_constructor'
    monitor = GenericMonitor(api_key=api_key_constructor)
    assert monitor._get_api_key() == api_key_constructor

# Test API key workflow when passed directly to the method
def test_api_key_passed_directly(monitor):
    api_key_pass = 'test_api_key_pass'
    assert monitor._get_api_key(api_key_pass) == api_key_pass
