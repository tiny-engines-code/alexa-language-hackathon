import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from source.model import StorageManager, FlashCard


class LocalStorage(StorageManager):
    def __init__(self, root_directory):
        super().__init__()
        self.root_directory = root_directory
        if not os.path.exists(root_directory):
            os.makedirs(root_directory)

    def check_file_exists(self, flash_card: FlashCard, base_name: str) -> bool:
        file_name = os.path.join(self.root_directory, flash_card.url, base_name)
        return self.check_exists(file_name=file_name)

    def check_exists(self, file_name):
        file_path = self.flash_card.url
        full_path = os.path.join(self.root_directory, file_path)
        return os.path.exists(full_path)

    def get_audio_url(self, flash_card):
        file_path = self.flash_card.url
        return os.path.join(self.root_directory, file_path)

    def read_translation(self, flash_card: FlashCard) -> str:
        file_name = os.path.join(self.root_directory, flash_card.url, self.flashcard_file)
        if not os.path.exists(file_name):
            return ""
        with open(file_name, "r") as fp:
            text = fp.read()
            json_flash = text

        flash_dict = json.loads(json_flash)
        id_value = flash_dict['id']
        source_phrase = flash_dict['source_phrase']
        dest_phrase = flash_dict['dest_phrase']
        if flash_card.id != id_value or flash_card.source_phrase != source_phrase:
            return ""
        flash_card.dest_phrase = dest_phrase
        return dest_phrase

    def write_translation(self, flash_card: FlashCard) -> bool:
        dir_name = os.path.join(self.root_directory, flash_card.url)
        file_name = os.path.join(dir_name, self.flashcard_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(file_name, "w") as fp:
            fp.write(flash_card.to_string())
        return True

    def write_audio(self, data: bytes) -> str:
        file_path = self.flash_card.url
        full_path = os.path.join(self.root_directory, file_path)

        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file = open(full_path, 'wb')
        file.write(data)
        file.close()
        self.flash_card.url = full_path
        return full_path

    def read_audio(self) -> (dict, bool):
        file_path = self.flash_card.url
        full_path = os.path.join(self.root_directory, file_path)
        return full_path
