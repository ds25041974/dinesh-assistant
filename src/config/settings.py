"""Configuration handling module."""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, Optional

from src.config.i18n import Language
from src.config.templates import TemplateManager
from src.config.validation import LogLevel, ValidationError, validate_config


@dataclass
class AppConfig:
    """Application configuration."""

    debug: bool = False
    log_level: str = LogLevel.INFO.value
    greeting_template: str = "default"
    custom_message: Optional[str] = None
    template_style: str = "default"
    async_mode: bool = False
    theme: str = "light"
    language: Language = Language.EN
    timezone: str = "UTC"
    rate_limit: int = 100
    cache_timeout: int = 3600  # 1 hour in seconds
    max_retries: int = 3
    _logger: Optional[logging.Logger] = field(default=None, repr=False)

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
        self._logger = None

    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance.

        Returns:
            Logger instance configured with current settings.
        """
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(self.log_level)
        return self._logger

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ValidationError: If configuration is invalid.
            KeyError: If template style doesn't exist.
        """
        # First check if template exists to match test expectations
        if not TemplateManager.get_template_info(self.template_style):
            raise KeyError(f"Template style '{self.template_style}' not found")

        type_checks = {
            "debug": (self.debug, bool),
            "template_style": (self.template_style, str),
            "language": (self.language, Language),
            "async_mode": (self.async_mode, bool),
        }

        for field_name, (value, expected_type) in type_checks.items():
            if not isinstance(value, expected_type):
                raise ValidationError(
                    {field_name: f"Must be a {expected_type.__name__}"}
                )

        if self.custom_message is not None and not isinstance(self.custom_message, str):
            raise ValidationError({"custom_message": "Must be None or a string"})

        if self.log_level not in LogLevel.__members__:
            raise ValidationError({"log_level": f"Invalid log level: {self.log_level}"})

        # Run template validation last
        errors = validate_config(self)
        if errors:
            raise ValidationError({str(i): err for i, err in enumerate(errors)})

    @classmethod
    def from_file(cls, filepath: str) -> "AppConfig":
        """Load configuration from a JSON file.

        Args:
            filepath: Path to JSON config file.

        Returns:
            AppConfig instance.

        Raises:
            ValidationError: If loaded configuration is invalid.
        """
        if not os.path.exists(filepath):
            return cls()

        with open(filepath, "r") as f:
            data = json.load(f)
            # Convert language from string to enum if needed
            if "language" in data and isinstance(data["language"], str):
                try:
                    data["language"] = Language(data["language"])
                except ValueError:
                    raise ValidationError(
                        {"language": f"Invalid language value: {data['language']}"}
                    )
            config = cls(**data)
            # validate() is called in post_init
            return config

    def to_file(self, filepath: str) -> None:
        """Save configuration to a JSON file.

        Args:
            filepath: Path to save JSON config.
        """
        with open(filepath, "w") as f:
            data = self.to_dict()
            # Convert enums to string values for JSON
            if isinstance(data.get("language"), Language):
                data["language"] = data["language"].value
            json.dump(data, f, indent=2)

    def to_dict(self) -> Dict:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config.
        """
        return {k: v for k, v in asdict(self).items() if not k.startswith("_")}
