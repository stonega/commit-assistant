import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from assistant.config import Config


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory"""
    config_dir = tmp_path / "commit-assistant"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def config_with_temp_dir(temp_config_dir):
    """Create a Config instance with temporary directory"""
    with patch("assistant.config.Config") as mock_config:
        config = Config()
        config.config_dir = temp_config_dir
        config.config_file = temp_config_dir / "coas.conf"
        return config


def test_config_init():
    """Test Config initialization"""
    config = Config()
    assert config.config_dir == Path(os.path.expanduser("~/.config/commit-assistant"))
    assert config.config_file == config.config_dir / "coas.conf"


def test_default_config_values():
    """Test default configuration values"""
    config = Config()
    assert (
        config.get("database", "path") == "~/.local/config/commit-assistant/commits.db"
    )
    assert config.get("git", "hooks_dir") == ".husky"
    assert config.get("logging", "level") == "INFO"


def test_set_and_get_config(config_with_temp_dir):
    """Test setting and getting configuration values"""
    config = config_with_temp_dir
    config.set("test", "key", "value")
    assert config.get("test", "key") == "value"


def test_save_and_load_config(config_with_temp_dir):
    """Test saving and loading configuration"""
    config = config_with_temp_dir
    config.set("test", "key", "value")
    config.save()

    # Create new config instance to test loading
    new_config = Config()
    new_config.config_dir = config.config_dir
    new_config.config_file = config.config_file
    new_config._load_config()

    assert new_config.get("test", "key") == "value"


def test_config_file_creation(temp_config_dir):
    """Test config file is created with defaults if not exists"""
    with patch("assistant.config.Config.config_dir", temp_config_dir):
        config = Config()
        assert config.config_file.exists()
        assert (
            config.get("database", "path")
            == "~/.local/config/commit-assistant/commits.db"
        )


@patch("builtins.input", return_value="test_api_key")
def test_gemini_api_setup(mock_input, config_with_temp_dir):
    """Test Gemini API key setup"""
    config = config_with_temp_dir
    config.setup_gemini_api()
    assert config.get("gemini", "api_key") == "test_api_key"


@patch("builtins.input", return_value="")
def test_gemini_api_setup_empty_key(mock_input, config_with_temp_dir):
    """Test Gemini API key setup with empty input"""
    config = config_with_temp_dir
    with pytest.raises(SystemExit):
        config.setup_gemini_api()


def test_config_properties(config_with_temp_dir):
    """Test config property accessors"""
    config = config_with_temp_dir
    assert config.db_path == os.path.expanduser(config.get("database", "path"))
    assert config.hooks_dir == config.get("git", "hooks_dir")
    assert config.log_level == config.get("logging", "level")
    assert config.log_file == os.path.expanduser(config.get("logging", "file"))


def test_get_nonexistent_value(config_with_temp_dir):
    """Test getting non-existent configuration value"""
    config = config_with_temp_dir
    assert config.get("nonexistent", "key", "default") == "default"
