"""Internationalization support module."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class Language(str, Enum):
    """Supported languages."""

    EN = "en"
    ES = "es"
    FR = "fr"
    DE = "de"
    JA = "ja"


@dataclass
class Translations:
    """Translation strings for a language."""

    greeting_prefix: str
    greeting_suffix: str
    error_messages: Dict[str, str]


_TRANSLATIONS: Dict[Language, Translations] = {
    Language.EN: Translations(
        greeting_prefix="Hello",
        greeting_suffix="!",
        error_messages={
            "invalid_name": "Name cannot be empty",
            "invalid_template": "Invalid template style",
            "invalid_language": "Unsupported language",
        },
    ),
    Language.ES: Translations(
        greeting_prefix="¡Hola",
        greeting_suffix="!",
        error_messages={
            "invalid_name": "El nombre no puede estar vacío",
            "invalid_template": "Estilo de plantilla inválido",
            "invalid_language": "Idioma no soportado",
        },
    ),
    Language.FR: Translations(
        greeting_prefix="Bonjour",
        greeting_suffix="!",
        error_messages={
            "invalid_name": "Le nom ne peut pas être vide",
            "invalid_template": "Style de modèle invalide",
            "invalid_language": "Langue non supportée",
        },
    ),
    Language.DE: Translations(
        greeting_prefix="Hallo",
        greeting_suffix="!",
        error_messages={
            "invalid_name": "Name darf nicht leer sein",
            "invalid_template": "Ungültiger Vorlagenstil",
            "invalid_language": "Nicht unterstützte Sprache",
        },
    ),
    Language.JA: Translations(
        greeting_prefix="こんにちは",
        greeting_suffix="！",
        error_messages={
            "invalid_name": "名前を入力してください",
            "invalid_template": "無効なテンプレートスタイル",
            "invalid_language": "サポートされていない言語",
        },
    ),
}


def get_translation(language: Language) -> Translations:
    """Get translations for a language.

    Args:
        language: Language code.

    Returns:
        Translations for the language.

    Raises:
        ValueError: If language is not supported.
    """
    if language not in _TRANSLATIONS:
        raise ValueError(f"Language {language} is not supported")
    return _TRANSLATIONS[language]


def translate_error(error_key: str, language: Language) -> str:
    """Translate an error message.

    Args:
        error_key: Error message key.
        language: Target language.

    Returns:
        Translated error message.
    """
    translations = get_translation(language)
    return translations.error_messages.get(error_key, error_key)
