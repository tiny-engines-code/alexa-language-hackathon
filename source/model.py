import json
import os
from abc import abstractmethod


class FlashCard:
    def __init__(self, conjugated: str, infinitive: str, source_lang: str, source_phrase: str, tense: str,
                 conjugation_id: str, expression_id: str, pronoun: str):
        self.id = f"{pronoun}-{conjugation_id}-{expression_id}"
        # self.conjugated_verb = conjugated
        self.infinitive_form = "to " + infinitive
        self.source_lang = source_lang
        self.tense = tense
        self.pronoun = pronoun.title()
        self.source_phrase = pronoun.title() + " " + conjugated + " " + source_phrase
        self.dest_lang = None
        self.dest_phrase = None
        self.dest_voice = None
        self.buffer = None
        self.url = None
        self.dest_mp3_url = None

    def set_destination(self, dest_lang, dest_voice):
        self.dest_lang = dest_lang
        self.dest_voice = dest_voice
        path = os.path.join(f"{self.source_lang}-{self.dest_lang}", self.dest_voice,
                            self.infinitive_form.replace(" ", "-"), self.tense)
        self.url = f"{path}/{self.id}/"

    def to_string(self):
        return json.dumps(self.__dict__)

    def from_json(self):
        return json.dumps(self.__dict__)


class StorageManager:
    flashcard_file = "flash_card.json"
    mp3_file = "vocal.mp3"

    def __init__(self):
        self.flash_card = None

    def set_flash_card(self, flash_card: FlashCard):
        self.flash_card = flash_card

    @abstractmethod
    def read_translation(self, flash_card: FlashCard) -> str:
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def write_translation(self, flash_card: FlashCard) -> bool:
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def get_audio_url(self, flash_card):
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def write_audio(self, flash_card: FlashCard, buffer: bytes) -> str:
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def read_audio(self) -> (dict, bool):
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def check_file_exists(self, flash_card: FlashCard, base_name: str) -> bool:
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def check_exists(self, file_name: str) -> bool:
        raise Exception("Cannot call abstract method")


class AudioPlayer:

    @abstractmethod
    def play_audio(self, url: bytes):
        # call self.url_manager.get_audio_url(flashcard)
        # if not exists:
        #    create audio with Polly
        #    self.url_manager.create_audio_url(flash_card)
        # play(url)
        raise Exception("Cannot call abstract method")
