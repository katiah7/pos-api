from pathlib import Path

import pytest
from pydantic import ValidationError

from core.config import Settings

SETTING_VARS = ["DATABASE_URL", "SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]


@pytest.fixture
def clean_env(monkeypatch):
    """Remove every setting from the environment so each test starts blank."""
    for name in SETTING_VARS:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_settings_are_read_from_environment_variables(clean_env):
    clean_env.setenv("DATABASE_URL", "postgresql://u:p@db:5432/shop")
    clean_env.setenv("SECRET_KEY", "abc123")
    settings = Settings(_env_file=None)
    assert settings.database_url == "postgresql://u:p@db:5432/shop"
    assert settings.secret_key == "abc123"


def test_token_settings_have_defaults(clean_env):
    clean_env.setenv("DATABASE_URL", "sqlite://")
    clean_env.setenv("SECRET_KEY", "abc123")
    settings = Settings(_env_file=None)
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 15


def test_token_settings_can_be_overridden(clean_env):
    clean_env.setenv("DATABASE_URL", "sqlite://")
    clean_env.setenv("SECRET_KEY", "abc123")
    clean_env.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    assert Settings(_env_file=None).access_token_expire_minutes == 30


def test_missing_secret_key_stops_the_app(clean_env):
    clean_env.setenv("DATABASE_URL", "sqlite://")
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)
    assert "secret_key" in str(error.value)


def test_missing_database_url_stops_the_app(clean_env):
    clean_env.setenv("SECRET_KEY", "abc123")
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)
    assert "database_url" in str(error.value)


def test_settings_can_be_read_from_a_dotenv_file(clean_env, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DATABASE_URL=postgresql://a:b@host/db\n"
        "SECRET_KEY=from-the-file\n"
        "ACCESS_TOKEN_EXPIRE_MINUTES=45\n"
    )
    settings = Settings(_env_file=env_file)
    assert settings.database_url == "postgresql://a:b@host/db"
    assert settings.secret_key == "from-the-file"
    assert settings.access_token_expire_minutes == 45


def test_environment_variables_override_the_dotenv_file(clean_env, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite://\nSECRET_KEY=from-the-file\n")
    clean_env.setenv("SECRET_KEY", "from-the-environment")
    assert Settings(_env_file=env_file).secret_key == "from-the-environment"


def test_unknown_keys_in_dotenv_are_ignored(clean_env, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite://\nSECRET_KEY=abc\nSOMETHING_ELSE=1\n")
    assert Settings(_env_file=env_file).secret_key == "abc"


def test_env_example_lists_the_required_settings():
    example = (Path(__file__).resolve().parent.parent / ".env.example").read_text()
    assert "DATABASE_URL=" in example
    assert "SECRET_KEY=" in example


def test_gitignore_keeps_the_real_env_file_out_of_git():
    gitignore = (Path(__file__).resolve().parent.parent / ".gitignore").read_text()
    assert ".env" in gitignore.splitlines()
