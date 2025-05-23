import json
import os

class Language:
    def __init__(self, default_language="en"):
        self.current_language = default_language  # Add current_language attribute
        self.translations = self.load_translations(default_language)

    def set_language(self, language_code):
        """Set the current language and load its translations."""
        self.current_language = language_code  # Update current_language
        self.translations = self.load_translations(language_code)

    def get_current_language(self):
        """Get the current language code."""
        return self.current_language

    def get(self, key):
        """Retrieve a translation for the given key."""
        return self.translations.get(key, key)

    def load_translations(self, language_code):
        """Load translations for the given language code."""
        base_path = os.path.dirname(__file__)
        lang_file = os.path.join(base_path, f"{language_code}.json")
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"Language file '{language_code}.json' not found.")
