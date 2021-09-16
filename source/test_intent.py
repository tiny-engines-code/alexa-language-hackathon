from typing import List, Dict
from uuid import uuid4

from ask_sdk_core.attributes_manager import AttributesManager
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import RequestEnvelope, IntentRequest, Intent, Slot, Status, Session
from ask_sdk_model.slu.entityresolution import Value, ValueWrapper, Resolution, Resolutions

from source.lambda_function import QuizHandler, QuizAnswerHandler


def create_test_slot(name, value, resolutions: List = None) -> Slot:
    values: List[ValueWrapper] = []
    resolution = Resolution(authority=str(uuid4()), status=Status(code='ER_SUCCESS_NO_MATCH'), values=None)
    if resolutions is not None and len(resolutions) > 0:
        for name in resolutions:
            values.append(ValueWrapper(Value(name=name, id=str(uuid4()))))
        resolution = Resolution(authority=str(uuid4()), status=Status(code='ER_SUCCESS_MATCH'), values=values)
    return Slot(name=name, value=value, resolutions=Resolutions(resolutions_per_authority=[resolution]))


def create_handler_input(slots: Dict[str, Slot], attributes: Dict) -> HandlerInput:
    request_envelope = RequestEnvelope(
        version="v1",
        session=Session(attributes=attributes),
        request=IntentRequest(request_id=str(uuid4()), intent=Intent(name="test intent", slots=slots)))
    attributes_manager = AttributesManager(request_envelope=request_envelope)
    handler_input = HandlerInput(
        request_envelope=request_envelope,
        attributes_manager=attributes_manager
    )
    return handler_input


def run_quiz_handler(slots: Dict[str, Slot], attributes: Dict) -> HandlerInput:
    handler_input = create_handler_input(slots=slots, attributes=attributes)
    response = QuizHandler().handle(handler_input=handler_input)
    return handler_input


def test_quiz_handler():
    # slots = {
    #     "game_type": create_test_slot(name="game_type", value="conjugation", resolutions=["conjugation"]),
    #     "tense": create_test_slot(name="tense", value="past future"),
    #     "verbs": create_test_slot(name="verbs", value="to be to have"),
    #     "plurality": create_test_slot(name="plurality", value="both"),
    #     "person": create_test_slot(name="person", value="3rd and 1st person"),
    # }
    slots = {
        "game_type": create_test_slot(name="game_type", value="conjugation", resolutions=["conjugation"]),
        "tense": create_test_slot(name="tense", value="all"),
        "verbs": create_test_slot(name="verbs", value="all"),
        "plurality": create_test_slot(name="plurality", value="all"),
        "person": create_test_slot(name="person", value="all"),
    }
    h_input = run_quiz_handler(slots=slots, attributes={"mode": "test"})
    h_attr = h_input.attributes_manager.session_attributes
    v = ["past", "future"].sort() == h_attr['tense'].sort()
    v = "random" == h_attr['game_type']
    v = ["be", "have"].sort() == h_attr['verbs'].sort()
    v = ["they", "we", "he", "i"].sort() == h_attr['pronouns'].sort()
    return h_input


def run_answer_handler(handler) -> HandlerInput:
    QuizAnswerHandler().handle(handler_input=handler)
    return handler_input


def test_answer_handler(handler):
    handler_input2 = run_answer_handler(handler=handler)
    # attr = handler_input2.attributes_manager.session_attributes
    # print("-----")
    # v = 2 == attr['counter']


if __name__ == "__main__":
    handler_input = test_quiz_handler()
    working = True
    while working:
        run_answer_handler(handler=handler_input)
        attr = handler_input.attributes_manager.session_attributes
        state = attr['state']
        if state != "DECK_QUEUED":
            working = False
