import pytest
from common_code.config import get_settings


def test_logger(caplog: pytest.LogCaptureFixture):
    from common_code.logger.logger import get_logger
    logger = get_logger(get_settings())
    caplog.set_level("INFO")
    logger.set_level("INFO")
    logger.info(message="test_info")
    assert "test_info" in caplog.text
    caplog.set_level("WARNING")
    logger.set_level("WARNING")
    logger.warning(message="test_warning")
    assert "test_warning" in caplog.text
    caplog.set_level("ERROR")
    logger.set_level("ERROR")
    logger.error(message="test_error")
    assert "test_error" in caplog.text
    caplog.set_level("CRITICAL")
    logger.set_level("CRITICAL")
    logger.critical(message="test_critical")
    assert "test_critical" in caplog.text
    caplog.set_level("DEBUG")
    logger.set_level("DEBUG")
    logger.debug(message="test_debug")
    assert "test_debug" in caplog.text
