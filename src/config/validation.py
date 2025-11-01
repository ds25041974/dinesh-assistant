"""Configuration validation module."""

from enum import Enum
from typing import Any, Dict, List, Protocol, runtime_checkable

from src.config.i18n import Language


@runtime_checkable
class ConfigProtocol(Protocol):
    """Protocol for configuration objects."""

    _debug: bool
    log_level: str
    _template_style: str
    _language: Language


class LogLevel(str, Enum):
    """Valid log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationError(Exception):
    """Configuration validation error."""

    def __init__(self, errors: Dict[str, str]):
        """Initialize validation error.

        Args:
            errors: Dictionary of field names and error messages.
        """
        self.errors = errors
        super().__init__(f"Configuration validation failed: {errors}")


def validate_config(config: Any) -> List[str]:
    """Validate configuration fields.

    Args:
        config: Configuration object to validate.

    Returns:
        List of validation error messages.
    """
    errors = []

    # Validate log level
    if not hasattr(config, "log_level") or config.log_level not in LogLevel.__members__:
        errors.append(f"Invalid log level: {getattr(config, 'log_level', None)}")

    # Validate template style
    from src.config.templates import TemplateManager

    if (
        not hasattr(config, "template_style")
        or config.template_style not in TemplateManager.list_templates()
    ):
        errors.append(
            f"Invalid template style: {getattr(config, 'template_style', None)}"
        )

    # Validate language
    if not hasattr(config, "language"):
        errors.append("Language not specified")
    else:
        try:
            if not isinstance(config.language, Language):
                Language(config.language)
        except ValueError:
            errors.append(f"Invalid language: {config.language}")

    return errors
