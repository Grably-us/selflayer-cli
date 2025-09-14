"""Configuration management for SelfLayer TUI.

This module handles persistent storage of configuration data like API keys,
user preferences, and application settings. Data is stored in a secure
JSON file in the user's home directory.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

# Configure module logger
logger = logging.getLogger(__name__)

# Configuration directory and file paths
CONFIG_DIR = Path.home() / ".selflayer"
CONFIG_FILE = CONFIG_DIR / "config.json"


class SelfLayerConfig(BaseModel):
    """
    Configuration model for SelfLayer TUI application.

    Stores persistent configuration data including API keys and user preferences.
    """

    api_key: Optional[str] = Field(
        default=None, description="SelfLayer API key for API access"
    )
    base_url: str = Field(
        default="https://api.selflayer.com/api/v1",
        description="Base URL for SelfLayer API",
    )
    log_level: str = Field(
        default="INFO", description="Logging level for the application"
    )
    created_at: Optional[str] = Field(
        default=None, description="Configuration creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, description="Configuration last update timestamp"
    )

    def has_api_key(self) -> bool:
        """Check if a valid API key is configured."""
        return self.api_key is not None and len(self.api_key.strip()) > 0

    def set_api_key(self, api_key: str) -> None:
        """Set the API key after validation."""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        # Validate API key format (SelfLayer keys start with sl_live_ or sl_test_)
        api_key = api_key.strip()
        if not (api_key.startswith("sl_live_") or api_key.startswith("sl_test_")):
            raise ValueError(
                "Invalid API key format. SelfLayer API keys must start with 'sl_live_' or 'sl_test_'"
            )

        self.api_key = api_key

    def clear_api_key(self) -> None:
        """Clear the stored API key."""
        self.api_key = None

    def get_masked_api_key(self) -> str:
        """Get a masked version of the API key for display."""
        if not self.api_key:
            return "Not set"

        if len(self.api_key) < 12:
            return "***"

        return f"{self.api_key[:8]}...{self.api_key[-4:]}"


class ConfigManager:
    """
    Manages configuration persistence for SelfLayer.

    Handles loading, saving, and updating configuration data stored in
    the user's home directory. Ensures secure storage with appropriate
    file permissions.
    """

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self._config: Optional[SelfLayerConfig] = None
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists with proper permissions."""
        try:
            CONFIG_DIR.mkdir(mode=0o700, exist_ok=True)
            logger.debug(f"Config directory ensured: {CONFIG_DIR}")
        except Exception as e:
            logger.warning(f"Failed to create config directory: {e}")

    def load_config(self) -> SelfLayerConfig:
        """
        Load configuration from disk.

        Returns:
            SelfLayerConfig object with loaded configuration or defaults
        """
        if self._config is not None:
            return self._config

        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Handle legacy format or missing fields
                if "created_at" not in config_data:
                    from datetime import datetime

                    config_data["created_at"] = datetime.utcnow().isoformat()

                # Handle legacy gemini_api_key field
                if "gemini_api_key" in config_data and "api_key" not in config_data:
                    config_data["api_key"] = config_data.pop("gemini_api_key")

                self._config = SelfLayerConfig(**config_data)
                logger.info("Configuration loaded successfully")
            else:
                from datetime import datetime

                self._config = SelfLayerConfig(created_at=datetime.utcnow().isoformat())
                logger.info("No existing config found, using defaults")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            from datetime import datetime

            self._config = SelfLayerConfig(created_at=datetime.utcnow().isoformat())

        return self._config

    def save_config(self, config: Optional[SelfLayerConfig] = None) -> bool:
        """
        Save configuration to disk.

        Args:
            config: Configuration to save (uses current config if None)

        Returns:
            True if save was successful, False otherwise
        """
        if config is not None:
            self._config = config

        if self._config is None:
            logger.error("No configuration to save")
            return False

        try:
            # Ensure directory exists
            self._ensure_config_dir()

            # Update timestamp
            from datetime import datetime

            self._config.updated_at = datetime.utcnow().isoformat()

            # Write config file with secure permissions
            config_data = self._config.model_dump(exclude_none=False)

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            # Set secure file permissions (readable/writable by owner only)
            CONFIG_FILE.chmod(0o600)

            logger.info("Configuration saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get_config(self) -> SelfLayerConfig:
        """Get the current configuration, loading it if necessary."""
        if self._config is None:
            return self.load_config()
        return self._config

    def update_api_key(self, api_key: str) -> bool:
        """
        Update the API key and save configuration.

        Args:
            api_key: New API key to store

        Returns:
            True if update and save were successful, False otherwise
        """
        try:
            config = self.get_config()
            config.set_api_key(api_key)
            return self.save_config(config)
        except Exception as e:
            logger.error(f"Failed to update API key: {e}")
            return False

    def clear_api_key(self) -> bool:
        """
        Clear the stored API key and save configuration.

        Returns:
            True if clear and save were successful, False otherwise
        """
        try:
            config = self.get_config()
            config.clear_api_key()
            return self.save_config(config)
        except Exception as e:
            logger.error(f"Failed to clear API key: {e}")
            return False

    def get_api_key(self) -> Optional[str]:
        """Get the stored API key."""
        config = self.get_config()
        return config.api_key

    def has_api_key(self) -> bool:
        """Check if a valid API key is configured."""
        config = self.get_config()
        return config.has_api_key()

    def get_config_file_path(self) -> Path:
        """Get the path to the configuration file."""
        return CONFIG_FILE

    def reset_config(self) -> bool:
        """
        Reset configuration to defaults and save.

        Returns:
            True if reset and save were successful, False otherwise
        """
        try:
            from datetime import datetime

            self._config = SelfLayerConfig(created_at=datetime.utcnow().isoformat())
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            return False

    def get_effective_api_key(self) -> Optional[str]:
        """
        Get the effective API key from config or environment.

        Prioritizes environment variable over stored config.

        Returns:
            API key string or None if not found
        """
        # Check environment first
        env_key = os.getenv("SELFLAYER_API_KEY")
        if env_key:
            return env_key.strip()

        # Fall back to stored config
        return self.get_api_key()

    def get_effective_base_url(self) -> str:
        """
        Get the effective base URL from config or environment.

        Returns:
            Base URL string
        """
        env_url = os.getenv("SELFLAYER_BASE_URL")
        if env_url:
            return env_url.strip()

        config = self.get_config()
        return config.base_url


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> SelfLayerConfig:
    """Get the current configuration."""
    return get_config_manager().get_config()


def save_api_key(api_key: str) -> bool:
    """Save an API key to persistent storage."""
    return get_config_manager().update_api_key(api_key)


def load_api_key() -> Optional[str]:
    """Load the API key from persistent storage."""
    return get_config_manager().get_api_key()


def get_effective_api_key() -> Optional[str]:
    """Get the effective API key (env var takes precedence over config)."""
    return get_config_manager().get_effective_api_key()


def has_stored_api_key() -> bool:
    """Check if there's a valid API key in storage."""
    return get_config_manager().has_api_key()


# Export public interface
__all__ = [
    "SelfLayerConfig",
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "save_api_key",
    "load_api_key",
    "get_effective_api_key",
    "has_stored_api_key",
]
