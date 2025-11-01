"""Template management module."""

import enum
from dataclasses import dataclass
from typing import Dict, Set


class TemplateCategory(enum.Enum):
    """Categories for greeting templates."""

    FORMAL = "formal"
    CASUAL = "casual"
    FUNNY = "funny"
    BUSINESS = "business"


@dataclass
class TemplateInfo:
    """Metadata for a template."""

    pattern: str
    category: TemplateCategory
    tags: Set[str]
    description: str


class TemplateManager:
    """Manages greeting templates with metadata."""

    _templates: Dict[str, TemplateInfo] = {
        "default": TemplateInfo(
            pattern="Hello, {name}! {message}",
            category=TemplateCategory.CASUAL,
            tags={"simple", "general"},
            description="A simple, casual greeting",
        ),
        "formal": TemplateInfo(
            pattern="Dear {name}, {message}",
            category=TemplateCategory.FORMAL,
            tags={"polite", "business"},
            description="A formal, professional greeting",
        ),
        "friendly": TemplateInfo(
            pattern="Hey {name}! {message}",
            category=TemplateCategory.CASUAL,
            tags={"informal", "friendly"},
            description="A friendly, informal greeting",
        ),
        "enthusiastic": TemplateInfo(
            pattern="Hi {name}! {message} 🎉",
            category=TemplateCategory.FUNNY,
            tags={"fun", "emoji"},
            description="An enthusiastic greeting with emoji",
        ),
    }

    @classmethod
    def list_templates(cls) -> Dict[str, TemplateInfo]:
        """List all available templates."""
        return cls._templates

    @classmethod
    def get_by_category(cls, category: TemplateCategory) -> Dict[str, TemplateInfo]:
        """Get templates by category.

        Args:
            category: The category to filter by.

        Returns:
            Dict of templates in the specified category.

        Raises:
            ValueError: If category is not a valid TemplateCategory.
        """
        if not isinstance(category, TemplateCategory):
            raise ValueError(f"Invalid category type: {type(category)}")
        return {
            name: info
            for name, info in cls._templates.items()
            if info.category == category
        }

    @classmethod
    def search_by_tags(cls, tags: Set[str]) -> Dict[str, TemplateInfo]:
        """Get templates that have any of the specified tags.

        Args:
            tags: Set of tags to search for.

        Returns:
            Dict of templates that match any of the tags.
        """
        return {
            name: info
            for name, info in cls._templates.items()
            if tags & info.tags  # intersection
        }

    @classmethod
    def get_template_info(cls, name: str) -> TemplateInfo:
        """Get metadata for a specific template.

        Args:
            name: Name of the template.

        Returns:
            Template info object.

        Raises:
            KeyError: If template doesn't exist.
        """
        return cls._templates[name]

    @classmethod
    def get_template(cls, name: str) -> str:
        """Get a template pattern by name.

        Args:
            name: Name of the template.

        Returns:
            Template pattern string.

        Raises:
            KeyError: If template doesn't exist.
        """
        return cls._templates[name].pattern
