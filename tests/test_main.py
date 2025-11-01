"""Tests for the main module."""

import asyncio
import os
import tempfile

import pytest

from src.config.i18n import Language, get_translation
from src.config.settings import AppConfig
from src.config.templates import TemplateCategory, TemplateManager
from src.config.validation import ValidationError
from src.main import async_greet, greet, list_templates


def test_greet_default() -> None:
    """Test the greet function with default settings."""
    translations = get_translation(Language.EN)
    assert greet("World") == f"{translations.greeting_prefix}, World! "


def test_greet_template_style() -> None:
    """Test the greet function with different template styles."""
    config = AppConfig(template_style="friendly")
    assert greet("World", config) == "Hey World! "


def test_greet_with_custom_message() -> None:
    """Test the greet function with custom message."""
    config = AppConfig(custom_message="Have a great day!")
    translations = get_translation(Language.EN)
    assert (
        greet("World", config)
        == f"{translations.greeting_prefix}, World! Have a great day!"
    )


def test_greet_with_language() -> None:
    """Test greeting with different languages."""
    # Test Spanish
    config = AppConfig(language=Language.ES)
    assert greet("World", config) == "¡Hola, World! "

    # Test French
    config = AppConfig(language=Language.FR)
    assert greet("World", config) == "Bonjour, World! "

    # Test Japanese
    config = AppConfig(language=Language.JA)
    assert greet("World", config) == "こんにちは、World! "


def test_greet_debug_mode(caplog) -> None:
    """Test the greet function in debug mode."""
    config = AppConfig(debug=True)
    result = greet("World", config)
    translations = get_translation(Language.EN)
    assert result == f"{translations.greeting_prefix}, World! "
    assert "Generating greeting for World" in caplog.text


@pytest.mark.asyncio
async def test_async_greet() -> None:
    """Test async greeting function."""
    result = await async_greet("World")
    translations = get_translation(Language.EN)
    assert result == f"{translations.greeting_prefix}, World! "


def test_config_file_handling() -> None:
    """Test configuration file handling."""
    config = AppConfig(
        debug=True,
        custom_message="Test message",
        template_style="formal",
        language=Language.ES,
    )

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        config.to_file(f.name)
        loaded_config = AppConfig.from_file(f.name)

        assert loaded_config.debug == config.debug
        assert loaded_config.custom_message == config.custom_message
        assert loaded_config.template_style == config.template_style
        assert loaded_config.language == config.language

        os.unlink(f.name)


def test_template_manager() -> None:
    """Test template manager functionality."""
    templates = TemplateManager.list_templates()

    # Test default template pattern
    assert templates["default"].pattern == "Hello, {name}! {message}"

    # Test template categories
    formal_templates = TemplateManager.get_by_category(TemplateCategory.FORMAL)
    assert "formal" in formal_templates
    assert formal_templates["formal"].category == TemplateCategory.FORMAL

    # Test template tags
    business_templates = TemplateManager.search_by_tags({"business"})
    assert "formal" in business_templates
    assert "polite" in business_templates["formal"].tags

    # Test template info
    info = TemplateManager.get_template_info("friendly")
    assert info.pattern == "Hey {name}! {message}"
    assert info.category == TemplateCategory.CASUAL
    assert info.description == "A friendly, informal greeting"


def test_language_support() -> None:
    """Test language support functionality."""
    # Test English translations
    en_trans = get_translation(Language.EN)
    assert en_trans.greeting_prefix == "Hello"
    assert "invalid_name" in en_trans.error_messages

    # Test Japanese translations
    ja_trans = get_translation(Language.JA)
    assert ja_trans.greeting_prefix == "こんにちは"
    assert "invalid_name" in ja_trans.error_messages

    # Test invalid language
    with pytest.raises(ValueError):
        # Create an invalid Language enum value
        Language("invalid")


def test_edge_cases() -> None:
    """Test edge cases and boundary conditions."""
    # Test empty name
    with pytest.raises(ValidationError):
        config = AppConfig()
        greet("", config)

    # Test very long name
    long_name = "a" * 1000
    result = greet(long_name)
    assert len(result) > 1000

    # Test special characters in name
    special_name = "!@#$%^&*()"
    result = greet(special_name)
    assert special_name in result

    # Test unicode characters in name
    unicode_name = "🌟 星"
    result = greet(unicode_name)
    assert unicode_name in result


def test_concurrent_greetings() -> None:
    """Test multiple async greetings concurrently."""

    async def test_multiple():
        names = ["Alice", "Bob", "Charlie", "David", "Eve"]
        tasks = [async_greet(name) for name in names]
        results = await asyncio.gather(*tasks)
        return results

    results = asyncio.run(test_multiple())
    assert len(results) == 5
    assert all(isinstance(r, str) for r in results)
    assert "Alice" in results[0]
    assert "Eve" in results[4]


def test_template_error_handling() -> None:
    """Test template error handling."""
    # Test invalid template style
    with pytest.raises(KeyError):
        config = AppConfig(template_style="nonexistent")
        greet("Test", config)

    # Test template with missing required variables
    with pytest.raises(KeyError):
        TemplateManager.get_template_info("invalid")

    # Test template category validation
    with pytest.raises(ValueError):
        # Create a non-enum value that can't be converted to TemplateCategory
        invalid_category = object()  # type: ignore
        TemplateManager.get_by_category(invalid_category)  # type: ignore


def test_config_validation() -> None:
    """Test configuration validation."""
    # We can't modify protected attributes directly, so let's test through the constructor
    with pytest.raises(ValidationError):
        AppConfig(debug="not_a_bool")  # type: ignore

    with pytest.raises(ValidationError):
        AppConfig(template_style=123)  # type: ignore

    with pytest.raises(ValidationError):
        AppConfig(language="invalid")  # type: ignore

    with pytest.raises(ValidationError):
        AppConfig(custom_message=123)  # type: ignore


def test_cli_output_capture(capsys) -> None:
    """Test CLI output capture."""
    # Test template listing
    list_templates()
    captured = capsys.readouterr()
    assert "default" in captured.out
    assert "Pattern" in captured.out

    # Test template listing with category filter
    list_templates(category="formal")
    captured = capsys.readouterr()
    assert "formal" in captured.out
    assert "business" in captured.out

    # Test template listing with tags
    list_templates(tags="business,polite")
    captured = capsys.readouterr()
    assert "formal" in captured.out


def test_performance_concurrent_load() -> None:
    """Test performance under concurrent load."""
    import time

    # Test concurrent greetings performance
    async def load_test() -> float:
        start_time = time.time()
        tasks = []
        for i in range(100):  # Test with 100 concurrent requests
            name = f"User{i}"
            tasks.append(async_greet(name))
        await asyncio.gather(*tasks)
        return time.time() - start_time

    # Run load test
    elapsed = asyncio.run(load_test())
    assert elapsed < 2.0  # Should complete 100 requests in under 2 seconds

    # Test template system performance
    start_time = time.time()
    for i in range(1000):  # Test with 1000 sequential template operations
        TemplateManager.list_templates()
        TemplateManager.get_by_category(TemplateCategory.FORMAL)
        TemplateManager.search_by_tags({"business"})
    template_time = time.time() - start_time
    assert template_time < 1.0  # Should complete in under 1 second


def test_memory_usage() -> None:
    """Test memory usage under load."""
    import sys

    def get_size(obj: object) -> int:
        """Get size of object and its children in bytes."""
        seen = set()  # Track objects to prevent cycles

        def sizeof(obj: object) -> int:
            if id(obj) in seen:
                return 0
            seen.add(id(obj))
            size = sys.getsizeof(obj)
            if hasattr(obj, "__dict__"):
                size += sizeof(obj.__dict__)
            if hasattr(obj, "__slots__"):
                size += sum(sizeof(getattr(obj, slot)) for slot in obj.__slots__)  # type: ignore
            return size

        return sizeof(obj)

    # Test template system memory usage
    templates = TemplateManager.list_templates()
    template_size = get_size(templates)
    assert template_size < 10000  # Should be under 10KB

    # Test greeting system memory usage
    configs = []
    messages = []
    total_size = 0

    # Create 100 different configurations and messages
    for i in range(100):
        config = AppConfig(
            template_style="formal" if i % 2 == 0 else "friendly",
            language=Language.EN if i % 3 == 0 else Language.ES,
            custom_message=f"Message {i}" if i % 2 == 0 else None,
        )
        message = greet(f"User{i}", config)
        configs.append(config)
        messages.append(message)
        total_size += get_size(config) + get_size(message)

    # Average size per config+message pair should be reasonable
    avg_size = total_size / 100
    assert avg_size < 1000  # Average size should be under 1KB per pair
