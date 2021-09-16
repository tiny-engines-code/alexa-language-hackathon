import boto3

from source.model import AudioPlayer, StorageManager, FlashCard
from source.translator import Translator


class Synthesiser(object):
    polly_client = boto3.Session(region_name='us-west-2').client('polly')

    def __init__(self, speed):
        self.speed = speed

    def synthesize_speech(self, flash_card: FlashCard) -> dict:
        ssml_text = """<speak><prosody rate="%s">%s</prosody></speak>""" % (self.speed, flash_card.dest_phrase)
        return self.polly_client.synthesize_speech(
            VoiceId=flash_card.dest_voice,
            OutputFormat='mp3',
            SampleRate="24000",
            TextType="ssml",
            Text=ssml_text)


class AudioManager(object):

    def __init__(self, player: AudioPlayer, storage_manager: StorageManager, translator: Translator, target_speed):
        self.storage_manager = storage_manager
        self.player = player
        self.translator = translator
        self.synthesiser = Synthesiser(target_speed)
        self.deck = []

    def play(self, flash_card: FlashCard):
        self.storage_manager.set_flash_card(flash_card=flash_card)
        if self.storage_manager.check_exists():
            url = self.storage_manager.read_audio()
        else:
            response = self.synthesiser.synthesize_speech(flash_card)
            url = self.storage_manager.write_audio(response['AudioStream'].read())

        self.player.play_audio(url=url)
        return self.storage_manager.flash_card

    def insert_translation(self, flash_card: FlashCard):
        # see if it's already translated and stored in storage, if not, store it
        if self.storage_manager.check_file_exists(flash_card=flash_card, base_name=self.storage_manager.flashcard_file):
            self.storage_manager.read_translation(flash_card)
        else:
            flash_card = self.translator.translate(flash_card)
            self.storage_manager.write_translation(flash_card)

        # see if the synthesized vocal is there, otherwise create it
        if self.storage_manager.check_file_exists(flash_card=flash_card, base_name=self.storage_manager.mp3_file):
            url = self.storage_manager.get_audio_url(flash_card=flash_card)
            flash_card.dest_mp3_url = url
        else:
            self.store_audio(flash_card=flash_card)

        # store the updated flash card in a deck
        self.deck.append(flash_card)

    def store_audio(self, flash_card: FlashCard) -> str:
        try:
            response = self.synthesiser.synthesize_speech(flash_card)
            url = self.storage_manager.write_audio(flash_card=flash_card, buffer=response['AudioStream'].read())
            flash_card.dest_mp3_url = url
            return url
        except Exception as e:
            print(e)
        return ""





