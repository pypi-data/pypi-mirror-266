"""Module for managing decks in Anki"""
import json
import logging
import random
import os
import requests
import genanki
from laoshi.flashcardgenerator import FlashCard

FIELDS_LIST = [
    {"name": "Simplified"},
    {"name": "Traditional"},
    {"name": "Pinyin"},
    {"name": "Translation"},
    {"name": "Sound"},
]

MODEL_CSS = """
.card {
    font-family: arial;
    font-size: 48px;
    text-align: center;
    color: black;
    background-color: white;
    line-height: 2em;
}
"""

ANSWER = '{{FrontSide}}<hr id="answer">{{Simplified}}<br>{{Traditional}} \
<br>{{Pinyin}}<br>{{Translation}}</div><br>{{Sound}}</div>'

CHINESE_TO_ENGLISH = genanki.Model(
    1459389108,
    "Chinese to English",
    fields=FIELDS_LIST,
    css=MODEL_CSS,
    templates=[
        {
            "name": "Card {{Simplified}} English to Chinese",
            "qfmt": '<div class="card">{{Simplified}}<br>{{Traditional}}',
            "afmt": ANSWER,
        },
    ],
)

ENGLISH_TO_CHINESE = genanki.Model(
    1313378830,
    "English to Chinese",
    fields=FIELDS_LIST,
    css=MODEL_CSS,
    templates=[
        {
            "name": "Card {{Simplified}} English to Chinese",
            "qfmt": '<div class="card">{{Translation}}',
            "afmt": ANSWER,
        },
    ],
)

AUDIO_ONLY = genanki.Model(
    1280077338,
    "Audio Only",
    fields=FIELDS_LIST,
    css=MODEL_CSS,
    templates=[
        {
            "name": "Card {{Simplified}} Audio",
            "qfmt": '<div class="card">{{Sound}}',
            "afmt": ANSWER,
        },
    ],
)


def get_unique_id() -> int:
    """Creates a unique ID"""
    return random.randrange(1 << 30, 1 << 31)


class DeckManager:
    """Manages and creates Anki Decks"""

    def __init__(self, deck_name: str, base_url: str = "http://localhost:8765"):
        """Init method"""
        self.deck_name = deck_name
        self.base_url = base_url

    def create_deck(self, flashcard: FlashCard):
        """Creates a deck from one FlashCard"""
        deck = genanki.Deck(get_unique_id(), self.deck_name)
        package = genanki.Package(deck)
        output = f"{deck.name}.apkg"
        deck.add_note(
            genanki.Note(
                guid=get_unique_id(),
                model=CHINESE_TO_ENGLISH,
                fields=flashcard.get_fields(),
            )
        )
        deck.add_note(
            genanki.Note(
                guid=get_unique_id(),
                model=ENGLISH_TO_CHINESE,
                fields=flashcard.get_fields(),
            )
        )
        deck.add_note(
            genanki.Note(
                guid=get_unique_id(), model=AUDIO_ONLY, fields=flashcard.get_fields()
            )
        )
        package.media_files = [flashcard.get_media_path()]
        package.write_to_file(output)

    def add_note(self, flashcard: FlashCard):
        """Adds a flashcard to the deck"""
        for model in [CHINESE_TO_ENGLISH, ENGLISH_TO_CHINESE, AUDIO_ONLY]:
            fjson = self.create_json(flashcard, model.name).encode("utf8")
            result = requests.post(self.base_url, fjson, timeout=30)
            if result.status_code != 200:
                logging.warning(
                    f"Error creating note {flashcard.simplified}!" + f"{result.reason}"
                )

    def create_json(self, flashcard: FlashCard, model_name: str) -> str:
        """Creates a json from a flashcard object with the model name"""
        result = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": self.deck_name,
                    "modelName": model_name,
                    "fields": {
                        "Simplified": flashcard.simplified,
                        "Traditional": flashcard.traditional,
                        "Pinyin": flashcard.pinyin,
                        "Translation": flashcard.translation,
                    },
                    "options": {
                        "allowDuplicate": False,
                        "duplicateScope": "deck",
                        "duplicateScopeOptions": {
                            "deckName": "Default",
                            "checkChildren": False,
                            "checkAllModels": False,
                        },
                    },
                    "tags": [],
                    "audio": [
                        {
                            "path": flashcard.sound_path,
                            "filename": flashcard.sound_file,
                            "fields": ["Sound"],
                        }
                    ],
                }
            },
        }
        return json.dumps(result, ensure_ascii=False)

    def close(self):
        """Deletes the deck if needed"""
        output = f"{self.deck_name}.apkg"
        if os.path.exists(output):
            os.remove(output)
