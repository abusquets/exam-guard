from config import settings


def test_seetings() -> None:
    assert settings.APP_ENV == 'test'
