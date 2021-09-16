"""
    "es-ES": dict(VoiceId='Conchita', TargetLanguageCode="es"),
    "es-MX": dict(VoiceId='Mia', TargetLanguageCode="es"),
    "es-US": dict(VoiceId='Lupe', TargetLanguageCode="es"),
    "it-IT": dict(VoiceId='Giorgio', TargetLanguageCode="it"),
    "fr-FR": dict(VoiceId='Mathieu', TargetLanguageCode="fr"),
    "fr-CA": dict(VoiceId='Chantal', TargetLanguageCode="fr")

"""
from typing import List

from source.audio_manager import AudioManager
from source.configure import Configuration
from source.database import Database
from source.translator import Translator

personas = {
    "first": {"plural": "we", "singular": "i"},
    "second": {"plural": "you", "singular": "you"},
    "third": {"plural": "they", "singular": "he"}
}



def parse_pronouns(request_string: str) -> List[str]:
    words = request_string
    person = list(filter(lambda x: x in ("first", "second", "third"), words))
    pluralism = "plural" if "plural" in words else "singular"
    pronouns = []
    for p in person:
        try:
            pronouns.append(personas[p][pluralism])
        except:
            pass

    pronoun_list = list(
        map(lambda y: f"""'{y}'""", pronouns))
    return pronoun_list


def parse_verbs(request_string: str) -> List[str]:
    words = request_string
    verbs = {}
    v_clause = False
    for i in range(len(words)):
        word = words[i]
        if word in ("verb", "verbs"):
            v_clause = True
        if v_clause and word == "to" and i + 1 < len(words):
            verbs[words[i + 1]] = i + 1
    return list(verbs.keys())


def parse_tenses(request_string: str) -> List[str]:
    words = request_string
    return list(
        map(lambda y: f"""'{y}'""",
            filter(lambda x: x in ("future", "past", "present"), words)))


def parse_request(request_string):
    words = request_string
    pronouns = parse_pronouns(words)
    tenses = parse_tenses(words)
    verbs = parse_verbs(words)


def handle_start_request(request_string):
    pass


def start():
    # start asking questions
    # valid state = collecting
    pass


def next_flash_card():
    # go to next
    # valid state = in-progress
    pass


def previous_flash_card():
    # go to previous
    # valid state = in-progress
    pass


def repeat_flash_card():
    # go to previous
    # valid state = in-progress
    pass


def cancel_session():
    # end asking questions
    # valid state = any
    pass


def get_strict(dictionary: dict, key: str):
    try:
        return dictionary[key]
    except Exception as err:
        raise Exception(f"{key} is not a valid argument - ${repr(err)}")
