from source.model import AudioPlayer


class AlexaPlayer(AudioPlayer):
    def play_audio(self, url: bytes):
        print("ALEXA PLAYING ", url)
