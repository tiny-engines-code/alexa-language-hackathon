# -*- coding: utf-8 -*-

# IMPORTANT: Please note that this template uses Display Directives,
# Display Interface for your skill should be enabled through the Amazon
# developer console
# See this screen shot - https://alexa.design/enabledisplay

import json
import logging
from typing import List

from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model import Response

from source.alexa_skill_surface import marshal_request, generate_dynamic_cards, fetch_dynamic_cards
from source.model import FlashCard

PROGRAM_NAME = "verb-flashcards"
WELCOME_MESSAGE = "Let's play!"
HELP_MESSAGE = f"{PROGRAM_NAME} provides a set of flash cards based on your requirements.  " \
               f"Each flash card will say a phrase in the source language, then pause for your response.  " \
               f"{PROGRAM_NAME} will then say the same phrase in the destination language"

EXIT_SKILL_MESSAGE = f"Thanks for playing {PROGRAM_NAME}"
START_QUIZ_MESSAGE = "Let's get this party started. "
MAX_FLASHCARDS = 10
FALLBACK_ANSWER = "I can't help you."

# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

personas = {
    "first": {"plural": "we", "singular": "i"},
    "second": {"plural": "you", "singular": "you"},
    "third": {"plural": "they", "singular": "he"}
}


# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        handler_input.response_builder.speak(WELCOME_MESSAGE).ask(
            HELP_MESSAGE)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        handler_input.attributes_manager.session_attributes = {}
        # Resetting session

        handler_input.response_builder.speak(
            HELP_MESSAGE).ask(HELP_MESSAGE)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak(
            EXIT_SKILL_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


class QuizHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("QuizIntent")(handler_input) or
                is_intent_name("AMAZON.StartOverIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In QuizHandler")

        # parse out request parameters
        params = marshal_request(handler_input.request_envelope.request.intent.slots)

        # add parsed request parameters to the session attributes
        attr = handler_input.attributes_manager.session_attributes
        attr.update(params)

        # generate a set of cards
        generate_dynamic_cards(session_attributes=attr)

        # prompt the user to continue
        question = "What's your favorite color?"
        response_builder = handler_input.response_builder
        response_builder.speak(START_QUIZ_MESSAGE + question)
        response_builder.ask(question)
        return response_builder.response


class QuizAnswerHandler(AbstractRequestHandler):
    """Handler for answering the quiz.
    The ``handle`` method will check if the answer specified is correct,
    by checking if it matches with the corresponding session attribute
    value. According to the type of answer, alexa responds to the user
    with either the next question or the final score.
    Similar to the quiz handler, the question choices are
    added to the Card or the RenderTemplate after checking if that
    is supported.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return is_intent_name("AnswerIntent")(handler_input)

    # def check_page(self, handler_input):
    #     # valid states: REQUESTED, IN-PROGRESS
    #     attr = handler_input.attributes_manager.session_attributes
    #
    #     # get the current flashcard
    #     if 'deck' not in attr:
    #         raise Exception("In answer method, but no decked was queued ")
    #     deck: List[FlashCard] = attr['deck']
    #     deck_size: int = len(deck)
    #     counter: int = int(attr['counter'])
    #
    #     # If we are finished with the current page and need to fetch the next page
    #     if len(deck) == 0:
    #         generate_dynamic_cards(attr)
    #
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # valid states: REQUESTED, IN-PROGRESS
        logger.info("In QuizAnswerHandler Version 7")

        # self.check_page(handler_input=handler_input)
        current_id = None
        response_builder = handler_input.response_builder
        response_builder.speak("more?")
        attr = handler_input.attributes_manager.session_attributes
        if attr['state'] != 'DECK_QUEUED':
            response_builder.set_should_end_session(True)
            response_builder.speak("bye")
        else:
            response_builder = handler_input.response_builder
            if 'deck' not in attr:
                raise Exception("In answer method, but no decked was queued ")
            deck: List[FlashCard] = attr['deck']
            if len(deck) == 0:
                fetch_dynamic_cards(attr)

            deck: List[FlashCard] = attr['deck']
            if len(deck) == 0:
                print("Zero pull from cards")
                current_id = None
                response_builder.set_should_end_session(True)
                response_builder.speak("bye")
            else:
                flash_card = deck[0]
                current_id = flash_card.id

                index = 0
                if 'flow' in attr:
                    index = attr['flow']  # 0=start, 1=source_phrase, 2=dest_phrase, 3=done
                if index == 0:
                    attr['flow'] = 1
                    response_builder.speak(flash_card.source_phrase).ask("in english")
                    response_builder.set_should_end_session(False)
                elif index == 1:
                    url = flash_card.dest_mp3_url
                    # play(url)
                    print(f"Play: {flash_card.dest_phrase} .. {url}")
                    print("---")
                    deck.pop(0)
                    attr['flow'] = 0
                    attr["counter"] += 1
                    if len(deck) == 0:
                        fetch_dynamic_cards(attr)

                    deck: List[FlashCard] = attr['deck']
                    if len(deck) == 0:
                        response_builder.speak("That's all in this set.  Bye!")
                        response_builder.set_should_end_session(True)
                    else:
                        attr['flow'] = 0
                        flash_card = deck[0]
                        current_id = flash_card.id
                        response_builder.speak("next?")
                        response_builder.set_should_end_session(False)

            response = response_builder.response
            if current_id is not None:
                print(f"Id: {current_id}, Speak: {response.output_speech.ssml}")
            # print(f"Ask: {response.reprompt.output_speech.ssml}")
            return response


class RepeatHandler(AbstractRequestHandler):
    """Handler for repeating the response to the user."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RepeatHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder
        if "recent_response" in attr:
            cached_response_str = json.dumps(attr["recent_response"])
            cached_response = DefaultSerializer().deserialize(
                cached_response_str, Response)
            return cached_response
        else:
            response_builder.speak("I can't help you.").ask(HELP_MESSAGE)

            return response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent.
     2018-May-01: AMAZON.FallackIntent is only currently available in
     en-US locale. This handler will not be triggered except in that
     locale, so it can be safely deployed for any locale."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler - Version 3")
        logger.info("FallbackIntentHandler V4: {}".format(
            handler_input.request_envelope.request.intent))
        handler_input.response_builder.speak(
            FALLBACK_ANSWER).ask(HELP_MESSAGE)

        return handler_input.response_builder.response


# Interceptor classes
class CacheResponseForRepeatInterceptor(AbstractResponseInterceptor):
    """Cache the response sent to the user in session.
    The interceptor is used to cache the handler response that is
    being sent to the user. This can be used to repeat the response
    back to the user, in case a RepeatIntent is being used and the
    skill developer wants to repeat the same information back to
    the user.
    """

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["recent_response"] = response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.
    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(QuizHandler())
sb.add_request_handler(QuizAnswerHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(FallbackIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_response_interceptor(CacheResponseForRepeatInterceptor())
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
