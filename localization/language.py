import json
import os

class Language:
    def __init__(self):
        self.translations = {}

    def load_language(self, lang_code):
        """Load the language file based on the given language code."""
        base_path = os.path.dirname(__file__)
        lang_file = os.path.join(base_path, f"{lang_code}.json")
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as file:
                self.translations = json.load(file)
        else:
            raise FileNotFoundError(f"Language file '{lang_code}.json' not found.")

    def get(self, key):
        """Retrieve the translation for the given key."""
        return self.translations.get(key, key)
