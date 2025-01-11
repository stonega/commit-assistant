import os
import configparser
from pathlib import Path
from typing import Any


class Config:
    """Configuration manager for commit-assistant"""

    DEFAULT_CONFIG = {
        "gemini": {},
    }

    def __init__(self):
        self.config_dir = Path(os.path.expanduser("~/.config/commit-assistant"))
        self.config_file = self.config_dir / "coas.conf"
        self.parser = configparser.ConfigParser()
        self._load_config()

    def setup_gemini_api(self) -> None:
        """Setup Gemini API key interactively"""
        print("\nGemini API Setup")
        print("----------------")
        print("You need a Gemini API key to use this tool.")
        print("Get your API key from: https://aistudio.google.com/apikey\n")

        api_key = input("Please enter your Gemini API key: ").strip()

        if not api_key:
            raise SystemExit("API key is required. Setup cancelled.")

        self.set("gemini", "api_key", api_key)
        self.save()
        print("Gemini API key saved successfully!")

    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if not self.config_file.exists():
                # Create config directory and file if they don't exist
                self.config_dir.mkdir(parents=True, exist_ok=True)
                # Save default configuration to file
                self.save()
                print(f"Created new config file at: {self.config_file}")
            else:
                self.parser.read(self.config_file)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Continue with default values

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get a configuration value"""
        try:
            value = self.parser.get(section, key)
            if section == "gemini" and key == "api_key" and not value:
                self.setup_gemini_api()
                value = self.parser.get(section, key)
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            if section == "gemini" and key == "api_key":
                self.setup_gemini_api()
                return self.parser.get(section, key)
            return fallback

    def set(self, section: str, key: str, value: str) -> None:
        """Set a configuration value"""
        if section not in self.parser:
            self.parser[section] = {}
        self.parser[section][key] = value

    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                self.parser.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")

    @property
    def db_path(self) -> str:
        """Get database path"""
        path = self.get("database", "path")
        return os.path.expanduser(path)

    @property
    def hooks_dir(self) -> str:
        """Get hooks directory"""
        return self.get("git", "hooks_dir")

    @property
    def log_level(self) -> str:
        """Get logging level"""
        return self.get("logging", "level")

    @property
    def log_file(self) -> str:
        """Get log file path"""
        path = self.get("logging", "file")
        return os.path.expanduser(path)


# Global config instance
config = Config()

if __name__ == "__main__":
    # Example usage
    print(f"Database path: {config.db_path}")
    print(f"Hooks directory: {config.hooks_dir}")
    print(f"Log level: {config.log_level}")
    print(f"Log file: {config.log_file}")
