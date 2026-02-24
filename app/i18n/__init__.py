import json
from pathlib import Path

_translations: dict[str, dict[str, str]] = {}
_current_lang = "ru"

I18N_DIR = Path(__file__).parent


def load_translations():
    global _translations
    for lang_dir in I18N_DIR.iterdir():
        if lang_dir.is_dir() and (lang_dir / "messages.json").exists():
            with open(lang_dir / "messages.json", encoding="utf-8") as f:
                _translations[lang_dir.name] = json.load(f)


def _(key: str, lang: str | None = None, **kwargs) -> str:
    lang = lang or _current_lang
    translations = _translations.get(lang, {})
    text = translations.get(key, _translations.get("en", {}).get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def set_language(lang: str):
    global _current_lang
    _current_lang = lang


def get_available_languages() -> list[dict[str, str]]:
    return [
        {"code": "ru", "name": "Русский"},
        {"code": "en", "name": "English"},
        {"code": "kz", "name": "Қазақша"},
        {"code": "tr", "name": "Türkçe"},
    ]


load_translations()
