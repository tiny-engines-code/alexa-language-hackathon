from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.response import Response
from ask_sdk_model.ui import StandardCard, Image, SimpleCard
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective)
from ask_sdk_model.interfaces import display

# The data for the gist is picked up from the single stream node audioplayer sample
# (https://github.com/alexa/skill-sample-nodejs-audio-player/tree/mainline/single-stream)

en_us_audio_data = {
    "card": {
        "title": 'My Radio',
        "text": 'Less bla bla bla, more la la la',
        "small_image_url": 'https://alexademo.ninja/skills/logo-108.png',
        "large_image_url": 'https://alexademo.ninja/skills/logo-512.png'
    },
    "url": 'https://audio1.maxi80.com',
    "start_jingle": 'https://s3-eu-west-1.amazonaws.com/alexa.maxi80.com/assets/jingle.m4a'
}


class AudioPlayIntentHandler(AbstractRequestHandler):
    # Handler for Audioplayer Play Intent
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AudioPlayIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Welcome to audioplayer sample"

        card = StandardCard(
            title=en_us_audio_data["card"]["title"],
            text=en_us_audio_data["card"]["text"],
            image=Image(
                small_image_url=en_us_audio_data["card"]["small_image_url"],
                large_image_url=en_us_audio_data["card"]["large_image_url"]
            )
        )

        directive = PlayDirective(
            play_behavior=PlayBehavior.REPLACE_ALL,
            audio_item=AudioItem(
                stream=Stream(
                    expected_previous_token=None,
                    token=en_us_audio_data["url"],
                    url=en_us_audio_data["url"],
                    offset_in_milliseconds=0
                ),
                metadata=AudioItemMetadata(
                    title=en_us_audio_data["card"]["title"],
                    subtitle=en_us_audio_data["card"]["text"],
                    art=display.Image(
                        content_description=en_us_audio_data["card"]["title"],
                        sources=[
                            display.ImageInstance(
                                url="https://alexademo.ninja/skills/logo-512.png"
                            )
                        ]
                    ),
                    background_image=display.Image(
                        content_description=en_us_audio_data["card"]["title"],
                        sources=[
                            display.ImageInstance(
                                url="https://alexademo.ninja/skills/logo-512.png"
                            )
                        ]
                    )
                )
            )
        )

        handler_input.response_builder.speak(speech_text).set_card(
            card).add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioStopIntentHandler(AbstractRequestHandler):
    # Handler for Stop
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye"

        directive = StopDirective()

        handler_input.response_builder.speak(speech_text).add_directive(
            directive).set_should_end_session(True)

        return handler_input.response_builder.response