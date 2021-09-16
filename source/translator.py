import boto3

from source.model import FlashCard


class Translator(object):
    def __init__(self, source_lang_code, target_lang_code, voice):
        self.translate_client = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
        self.source_language_code = source_lang_code
        self.metadata = {}
        self.target_language_code = target_lang_code
        self.voice_id = voice

    def translate(self, flash_card: FlashCard):
        result = self.translate_client.translate_text(Text=flash_card.source_phrase,
                                                      SourceLanguageCode=flash_card.source_lang,
                                                      TargetLanguageCode=self.target_language_code)

        translated_text = result.get('TranslatedText')
        flash_card.dest_voice = self.voice_id
        flash_card.dest_phrase = translated_text
        flash_card.dest_lang = self.target_language_code
        return flash_card


