"""
Internationalization module for SuiJarvisBot.
Simple JSON-based locale system with per-user language preference.
"""
import json
import os

LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")
_locales = {}
_user_langs = {}
LANG_FILE = os.path.join(os.path.dirname(__file__), "data", "user_langs.json")

def _load_locales():
    """Load all locale files from locales/ directory."""
    global _locales
    for fname in os.listdir(LOCALES_DIR):
        if fname.endswith(".json"):
            lang = fname[:-5]  # "en.json" -> "en"
            with open(os.path.join(LOCALES_DIR, fname), encoding="utf-8") as f:
                _locales[lang] = json.load(f)

def _load_user_langs():
    """Load user language preferences from disk."""
    global _user_langs
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE, encoding="utf-8") as f:
                _user_langs = json.load(f)
        except:
            _user_langs = {}

def _save_user_langs():
    """Save user language preferences to disk."""
    os.makedirs(os.path.dirname(LANG_FILE), exist_ok=True)
    with open(LANG_FILE, "w", encoding="utf-8") as f:
        json.dump(_user_langs, f, ensure_ascii=False)

def get_lang(uid) -> str:
    """Get user language preference, default Chinese."""
    return _user_langs.get(str(uid), "cn")

def set_lang(uid, lang: str):
    """Set user language preference."""
    _user_langs[str(uid)] = lang
    _save_user_langs()

def _(key: str, uid, **kwargs) -> str:
    """
    Get localized text by key for a user.
    
    Usage:
        _("welcome", uid, name="John", address="0x...")
        _("swap_panel", uid)
    
    Falls back to English if key not found in user's language.
    Falls back to key itself if not found anywhere.
    """
    lang = get_lang(uid)
    
    # Try user's language first
    text = _locales.get(lang, {}).get(key)
    
    # Fallback to English
    if text is None:
        text = _locales.get("en", {}).get(key)
    
    # Fallback to key itself
    if text is None:
        return key
    
    # Apply format kwargs if provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    
    return text

# Initialize on import
_load_locales()
_load_user_langs()
