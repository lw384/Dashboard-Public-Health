def test_log_action_writes_logs(tmp_path, monkeypatch):
    from dashboard_public_health.infrastructure import logger as ld

    # override log path
    monkeypatch.setattr(ld, "LOG_DIR", tmp_path)
    monkeypatch.setattr(ld, "LOG_FILE", tmp_path / "test.log")
    ld.logger.handlers.clear()

    ld.logger = ld.get_logger()  # re-init logger

    @ld.log_action
    def dummy(a, b):
        return a + b

    dummy(2, 3)

    log_file = tmp_path / "test.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "CALL: dummy" in content
    assert "RETURN: dummy" in content
