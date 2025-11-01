"""Main module for the project."""

import argparse
import asyncio
import json
import logging
import sys
from typing import Optional

from src.config.i18n import Language, get_translation
from src.config.settings import AppConfig
from src.config.templates import TemplateCategory, TemplateManager
from src.config.validation import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def greet(name: str, config: Optional[AppConfig] = None) -> str:
    """Return a greeting message synchronously.

    Args:
        name: The name to greet.
        config: Optional configuration object.

    Returns:
        A greeting message.

    Raises:
        ValidationError: If name is empty or contains invalid characters.
        KeyError: If template style doesn't exist.
        ValueError: If language is not supported.
    """
    if not name or not name.strip():
        raise ValidationError({"name": "Name cannot be empty"})

    if len(name) > 1000:
        raise ValidationError({"name": "Name is too long (max 1000 characters)"})

    cfg = config or AppConfig()
    if cfg.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Generating greeting for %s", name)

    try:
        # Get language-specific translations
        translations = get_translation(cfg.language)
    except ValueError as e:
        logger.error("Language error: %s", e)
        raise

    try:
        # Get template and format with translations
        template = TemplateManager.get_template(cfg.template_style)
        if cfg.template_style == "default":
            # Special handling for default template with translations
            if cfg.language == Language.JA:
                template = "{prefix}、{name}! {message}"
            else:
                template = "{prefix}, {name}! {message}"
    except KeyError:
        logger.error("Template style '%s' not found", cfg.template_style)
        raise

    try:
        message = template.format(
            name=name,
            message=cfg.custom_message or "",
            prefix=translations.greeting_prefix,
            suffix=translations.greeting_suffix,
        )
    except (KeyError, ValueError) as e:
        logger.error("Template formatting error: %s", e)
        raise

    return message


async def async_greet(name: str, config: Optional[AppConfig] = None) -> str:
    """Return a greeting message asynchronously.

    Args:
        name: The name to greet.
        config: Optional configuration object.

    Returns:
        A greeting message.

    Raises:
        ValidationError: If name is empty or contains invalid characters.
        KeyError: If template style doesn't exist.
        ValueError: If language is not supported.
        asyncio.TimeoutError: If the operation takes too long.
    """
    try:
        # Set a timeout for the entire operation
        async with asyncio.timeout(5.0):  # 5 second timeout
            # Simulate some async processing
            await asyncio.sleep(0.1)
            return greet(name, config)
    except asyncio.TimeoutError:
        logger.error("Async greeting timed out for name: %s", name)
        raise
    except Exception as e:
        logger.error("Async greeting error: %s", e)
        raise


def list_templates(category: Optional[str] = None, tags: Optional[str] = None) -> None:
    """List available templates with optional filtering.

    Args:
        category: Optional category to filter by.
        tags: Optional comma-separated tags to filter by.

    Raises:
        ValueError: If category is invalid.
        ValidationError: If tags are malformed.
    """
    try:
        # Get templates based on filters
        if category:
            try:
                cat = TemplateCategory(category)
                templates = TemplateManager.get_by_category(cat)
            except ValueError:
                logger.error("Invalid category: %s", category)
                logger.info("Valid categories: %s", [c.value for c in TemplateCategory])
                raise
        elif tags:
            # Validate tags format
            if not all(t.strip() for t in tags.split(",")):
                raise ValidationError({"tags": "Empty tags are not allowed"})
            if len(tags.split(",")) > 10:
                raise ValidationError({"tags": "Too many tags (max 10)"})

            tag_set = {t.strip() for t in tags.split(",")}
            templates = TemplateManager.search_by_tags(tag_set)
        else:
            templates = (
                TemplateManager.list_templates()
            )  # Use public API instead of _templates

        # Display template information
        for name, info in templates.items():
            print(f"\n{name}:")
            print(f"  Pattern: {info.pattern}")
            print(f"  Category: {info.category.value}")
            print(f"  Tags: {', '.join(info.tags)}")
            print(f"  Description: {info.description}")

    except Exception as e:
        logger.error("Error listing templates: %s", e)
        raise


def main() -> None:
    """Main entry point with enhanced CLI interface."""
    try:
        parser = argparse.ArgumentParser(description="Advanced greeting application")
        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # Greet command
        greet_parser = subparsers.add_parser("greet", help="Generate a greeting")
        greet_parser.add_argument("name", help="Name to greet")
        greet_parser.add_argument(
            "--debug", action="store_true", help="Enable debug mode"
        )
        greet_parser.add_argument("--message", help="Additional custom message")
        greet_parser.add_argument("--config", help="Path to config file")
        greet_parser.add_argument(
            "--style",
            choices=list(TemplateManager.list_templates().keys()),
            default="default",
            help="Greeting style",
        )
        greet_parser.add_argument(
            "--language",
            choices=[lang.value for lang in Language],
            default=Language.EN.value,
            help="Greeting language",
        )
        greet_parser.add_argument(
            "--async", action="store_true", dest="async_mode", help="Use async mode"
        )
        greet_parser.add_argument(
            "--save-config", help="Save current settings to config file"
        )

        # List templates command
        list_parser = subparsers.add_parser(
            "templates", help="List available templates"
        )
        list_parser.add_argument("--category", help="Filter by category")
        list_parser.add_argument("--tags", help="Filter by tags (comma-separated)")

        # Config management command
        config_parser = subparsers.add_parser("config", help="Manage configuration")
        config_parser.add_argument("action", choices=["view", "save", "validate"])
        config_parser.add_argument("--file", help="Config file path")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        if args.command == "templates":
            try:
                list_templates(args.category, args.tags)
            except (ValueError, ValidationError) as e:
                logger.error("Template listing error: %s", e)
                sys.exit(1)
            return

        if args.command == "config":
            try:
                config = AppConfig.from_file(args.file) if args.file else AppConfig()
            except (IOError, json.JSONDecodeError) as e:
                logger.error("Error loading config file: %s", e)
                sys.exit(1)

            if args.action == "view":
                print(json.dumps(config.to_dict(), indent=2))
            elif args.action == "validate":
                try:
                    config.validate()
                    print("Configuration is valid")
                except ValidationError as e:
                    print("Configuration errors:")
                    for field, error in e.errors.items():
                        print(f"  {field}: {error}")
                    sys.exit(1)
            elif args.action == "save" and args.file:
                try:
                    config.to_file(args.file)
                    print(f"Configuration saved to {args.file}")
                except IOError as e:
                    logger.error("Error saving config file: %s", e)
                    sys.exit(1)
            return

        if args.command == "greet":
            try:
                # Load config from file if specified
                config = (
                    AppConfig.from_file(args.config) if args.config else AppConfig()
                )

                # Input validation
                if not args.name or not args.name.strip():
                    logger.error("Name cannot be empty")
                    sys.exit(1)

                if len(args.name) > 1000:
                    logger.error("Name is too long (max 1000 characters)")
                    sys.exit(1)

                # Override config with CLI arguments
                config.debug = args.debug or config.debug
                config.log_level = "DEBUG" if config.debug else "INFO"
                config.custom_message = args.message or config.custom_message
                config.template_style = args.style
                config.async_mode = args.async_mode
                config.language = Language(args.language)

                if config.debug:
                    logging.getLogger().setLevel(logging.DEBUG)
                    logger.debug("Debug mode enabled")

                if args.save_config:
                    try:
                        config.to_file(args.save_config)
                        logger.info("Configuration saved to %s", args.save_config)
                    except IOError as e:
                        logger.error("Error saving config: %s", e)
                        sys.exit(1)

                # Validate and generate greeting
                config.validate()
                if config.async_mode:
                    try:
                        result = asyncio.run(async_greet(args.name, config))
                    except asyncio.TimeoutError:
                        logger.error("Async greeting timed out")
                        sys.exit(1)
                    except Exception as e:
                        logger.error("Async greeting error: %s", e)
                        sys.exit(1)
                else:
                    result = greet(args.name, config)
                print(result)

            except ValidationError as e:
                logger.error("Validation error:")
                for field, error in e.errors.items():
                    logger.error("  %s: %s", field, error)
                sys.exit(1)
            except (IOError, json.JSONDecodeError) as e:
                logger.error("Config file error: %s", e)
                sys.exit(1)
            except Exception as e:
                logger.error("Unexpected error: %s", e)
                if config.debug:
                    logger.exception("Detailed error information:")
                sys.exit(1)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Critical error: %s", e)
        sys.exit(1)
