from pygame import mixer  # Load the popular external library

from source.model import AudioPlayer


class LocalPlayer(AudioPlayer):

    def play_audio(self, url: str):
        # Set chunk size of 1024 samples per data frame
        try:
            mixer.init()
            mixer.music.load(url)
            mixer.music.play()
        except Exception as e:
            print(e)
