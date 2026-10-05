from src.config import Settings


def test_defaults_are_safe():
    settings = Settings()
    settings.validate()
    assert settings.dry_run is True
    assert settings.paper_trading is True
