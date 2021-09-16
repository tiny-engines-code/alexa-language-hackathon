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

from lambda_utils import SlotInfo, convert_person_to_pronouns

PROGRAM_NAME = "verb-flashcards"
WELCOME_MESSAGE = "Let's play!"
HELP_MESSAGE = f"{PROGRAM_NAME} provides a set of flash cards based on your requirements.  " \
               f"Each flash card will say a phrase in the source language, then pause for your response.  " \
               f"{PROGRAM_NAME} will then say the same phrase in the destination language"

EXIT_SKILL_MESSAGE = f"Thanks for playing {PROGRAM_NAME}"
START_QUIZ_MESSAGE = "Let's get this party started. "
MAX_QUESTIONS = 10
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
    """Handler for starting a quiz.
    The ``handle`` method will initiate a quiz state and build a
    question randomly from the states data, using the util methods.
    If the skill can use cards, then the question choices are added to
    the card and shown in the Response. If the skill uses display,
    then the question is displayed using RenderTemplates.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("QuizIntent")(handler_input) or
                is_intent_name("AMAZON.StartOverIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In QuizHandler")
        slots = handler_input.request_envelope.request.intent.slots

        # parse user utterances
        tenses = SlotInfo.get_instance(slots, 'tense', ["past", "present", "future"])
        game_type = SlotInfo.get_instance(slots, 'game_type', ["conjugation"])
        verbs = SlotInfo.get_instance(slots, 'verbs', [])
        person = SlotInfo.get_instance(slots, 'person', ["first","second","third"])
        plurality = SlotInfo.get_instance(slots, 'plurality', ["singular", "plural"])

        # transpose person and plurality to pronouns (he, she, we, you...)
        person.resolved_values = convert_person_to_pronouns(person, plurality)

        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "REQUESTED"
        attr["offset"] = 0
        attr["tense"] = tenses.to_string()
        attr["game_type"] = game_type.to_string()
        attr["verbs"] = verbs.to_string()
        attr["pronouns"] = person.to_string()

        logger.info("attr:GAME-TYPE: {}".format(attr["game_type"]))
        logger.info("attr:TENSE: {}".format(attr["tense"]))
        logger.info("attr:PRONOUNS: {}".format(attr["pronouns"]))
        logger.info("attr:VERBS: {}".format(attr["verbs"]))

        logger.info("attr:PLURALS: {}".format(plurality.to_string()))

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
        return (is_intent_name("AnswerIntent")(handler_input) and
                attr.get("state") == "QUIZ")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In QuizAnswerHandler Version 7")
        attr = handler_input.attributes_manager.session_attributes

        answer = handler_input.request_envelope.request.intent.slots['text']
        logger.info("QuizAnswerHandler NAME V4: {}".format(
            answer.name))
        logger.info("QuizAnswerHandler VALUE V4: {}".format(
            answer.value))

        logger.info("QuizAnswerHandler NAME V4: {}".format(
            handler_input.request_envelope.request.intent.slots['text']))

        logger.info("QuizAnswerHandler VALUE V4: {}".format(
            handler_input.request_envelope.request.intent.slots['text']))

        logger.info("QuizAnswerHandler ATTR V4: {}".format(attr))

        response_builder = handler_input.response_builder
        attr["counter"] += 1
        item_count: int = int(attr["counter"])
        # item = attr["quiz_item"]
        # item_attr = attr["quiz_attr"]

        is_ans_correct = True

        if is_ans_correct:
            speech = "Fantastic genius. "
            attr["quiz_score"] += 1
            handler_input.attributes_manager.session_attributes = attr
        else:
            speech = "What a moron."

        if item_count < MAX_QUESTIONS:
            # Ask another question
            speech += "How about another? "
            question = "What's the weather like in hell?"
            speech += question
            reprompt = question

            # Update item and item_attr for next question
            # item = attr["quiz_item"]
            # item_attr = attr["quiz_attr"]
            return response_builder.speak(speech).ask(reprompt).response
        else:
            # Finished all questions.
            speech += "I am so done with you"
            speech += EXIT_SKILL_MESSAGE

            response_builder.set_should_end_session(True)
            return response_builder.speak(speech).response


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