"""
    "es-ES": dict(VoiceId='Conchita', TargetLanguageCode="es"),
    "es-MX": dict(VoiceId='Mia', TargetLanguageCode="es"),
    "es-US": dict(VoiceId='Lupe', TargetLanguageCode="es"),
    "it-IT": dict(VoiceId='Giorgio', TargetLanguageCode="it"),
    "fr-FR": dict(VoiceId='Mathieu', TargetLanguageCode="fr"),
    "fr-CA": dict(VoiceId='Chantal', TargetLanguageCode="fr")

"""
import logging
from typing import Dict

from source.alexa_skill_worker import get_strict
from source.audio_manager import AudioManager
from source.configure import Configuration
from source.database import Database
from source.lambda_utils import SlotInfo, convert_person_to_pronouns
from source.translator import Translator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

locales = {
    "english": ("en", "US"),
    "spanish": ("es", "MX"),
    "french": ("fr", "FR"),
    "italian": ("it", "IT")
}

dialects = {
    "mexico": "MX",
    "spain": "ES",
    "united states": "US",
    "italy": "IT",
    "france": "FR",
    "canadian": "CA"
}
voices = {
    "es-ES": 'Conchita',
    "es-MX": 'Mia',
    "es-US": 'Lupe',
    "it-IT": 'Giorgio',
    "fr-FR": 'Mathieu',
    "fr-CA": 'Chantal'
}

personas = {
    "first": {"plural": "we", "singular": "i"},
    "second": {"plural": "you", "singular": "you"},
    "third": {"plural": "they", "singular": "he"}
}


#
# this begins an intent to start a new collection of quiz's
# valid state: any
#
def marshal_request(slots):
    # type: (dict) -> dict
    logger.info("In QuizHandler")

    # merge in configurables
    configs = Configuration.get_instance()

    # parse user utterances
    tenses = SlotInfo.get_instance(slots, 'tense', ["past", "present", "future"])
    game_type = SlotInfo.get_instance(slots, 'game_type', ["conjugation"])
    verbs = SlotInfo.get_instance(slots, 'verbs', [])
    pronouns = SlotInfo.get_instance(slots, 'person', ["first", "second", "third"])
    plurality = SlotInfo.get_instance(slots, 'plurality', ["singular", "plural"])

    # transpose person and plurality to pronouns (he, she, we, you...)
    pronouns.resolved_values = convert_person_to_pronouns(pronouns, plurality)

    #
    # marshal user request to enumerated values
    source_lang = get_strict(locales, configs.source_language)[0]
    target = get_strict(locales, configs.target_language)
    target_lang = target[0]
    target_dialect = target[1]
    if configs.target_dialect is not None:
        target_dialect = get_strict(dialects, configs.target_dialect)
    locale = f"{target_lang}-{target_dialect}"
    voice = get_strict(voices, locale)

    # create the session state object
    return dict(
        state="REQUESTED",
        game_type=game_type.get_resolved_values()[0],
        source_language=source_lang,
        dest_language=target_lang,
        dialect=target_dialect,
        dest_locale=locale,
        voice=voice,
        speed=configs.get_configuration('language_speed', "slow"),
        pronouns=pronouns.get_resolved_values(),
        tense=tenses.get_resolved_values(),
        verbs=verbs.get_resolved_values(),
        offset=0,
        counter=0,
        page_size=configs.get_configuration('page_size', 15)
    )


def generate_dynamic_cards(session_attributes: Dict):
    # get the configurations
    # valid state = collecting or in-progress
    config = Configuration.get_instance()

    # get the Database
    verbs_db = Database.get_instance()

    # get query parameters from the session
    pronouns = None
    tense = None
    verb_list = None
    speed = config.get_configuration('language_speed', "slow")
    page_size_num = config.get_configuration('page_size', 15)
    game_type = "conjugation"
    offset_num = 0
    if 'pronouns' in session_attributes:
        pronouns = session_attributes['pronouns']
    if 'tense' in session_attributes:
        tense = session_attributes['tense']
    if 'verbs' in session_attributes:
        verb_list = session_attributes['verbs']
    if 'offset' in session_attributes:
        offset_num = int(session_attributes['offset'])
    if 'page_size' in session_attributes:
        page_size_num = int(session_attributes['page_size'])
    if 'speed' in session_attributes:
        speed = session_attributes['speed']
    if 'game_type' in session_attributes:
        game_type = session_attributes['game_type']

    # game type
    standard = True
    random = False
    distinct = False
    if game_type == "random":
        standard = False
        random = True
        distinct = False
    elif game_type == "ordered":
        standard = False
        random = False
        distinct = True

    # set the query to create dynamic flash cards from the database repository
    verbs_db.set_dynamic_cards_query(session_attributes["source_language"], pronouns, tense, verb_list, standard=standard, distinct=distinct, random=random)


    # # get the translator for the destination language
    # translator = Translator(source_lang_code=session_attributes["source_language"],
    #                         target_lang_code=session_attributes["dest_language"],
    #                         voice=session_attributes['voice'])
    #
    # # get configured player and file managers
    # storage_mgr = config.get_file_manager()  # get an s3 or local file manager
    # player = config.get_player()    # get an alexa or pygame player
    # audio_handler = AudioManager(player=player, storage_manager=storage_mgr, target_speed=speed, translator=translator)
    #
    # try:
    fetch_dynamic_cards(session_attributes)
    #     rows = verbs_db.query_dynamic_cards(page_size=page_size_num, offset=offset_num)
    #     if len(rows) == 0:
    #         session_attributes['deck'] = []
    #         session_attributes['state'] = "QUERY_COMPLETED"
    #         session_attributes['counter'] = 0
    #         return
    #
    #     for flash_card in rows:
    #         print("%r" % flash_card.to_string())
    #         flash_card.set_destination(translator.target_language_code, translator.voice_id)
    #         audio_handler.insert_translation(flash_card=flash_card)
    #         session_attributes['offset'] += 1
    #
    #     session_attributes['deck'] = audio_handler.deck
    #     session_attributes['state'] = "DECK_QUEUED"
    #     session_attributes['counter'] = 0

    # except Exception as er:
    #     print("deal with this error")
    #

def fetch_dynamic_cards(session_attributes: Dict):
    # get the configurations
    # valid state = collecting or in-progress
    config = Configuration.get_instance()

    # get the Database
    verbs_db = Database.get_instance()

    # get query parameters from the session
    # pronouns = None
    # tense = None
    # verb_list = None
    speed = config.get_configuration('language_speed', "slow")
    page_size_num = config.get_configuration('page_size', 15)
    game_type = "conjugation"
    # offset_num = 0
    # if 'pronouns' in session_attributes:
    #     pronouns = session_attributes['pronouns']
    # if 'tense' in session_attributes:
    #     tense = session_attributes['tense']
    # if 'verbs' in session_attributes:
    #     verb_list = session_attributes['verbs']
    if 'offset' in session_attributes:
        offset_num = int(session_attributes['offset'])
    if 'page_size' in session_attributes:
        page_size_num = int(session_attributes['page_size'])
    if 'speed' in session_attributes:
        speed = session_attributes['speed']
    if 'game_type' in session_attributes:
        game_type = session_attributes['game_type']

    # game type
    # standard = True
    # random = False
    # distinct = False
    # if game_type == "random":
    #     standard = False
    #     random = True
    #     distinct = False
    # elif game_type == "ordered":
    #     standard = False
    #     random = False
    #     distinct = True

    # set the query to create dynamic flash cards from the database repository
    # verbs_db.set_dynamic_cards_query(session_attributes["source_language"], pronouns, tense, verb_list, standard=standard, distinct=distinct, random=random)

    # get the translator for the destination language
    translator = Translator(source_lang_code=session_attributes["source_language"],
                            target_lang_code=session_attributes["dest_language"],
                            voice=session_attributes['voice'])

    # get configured player and file managers
    storage_mgr = config.get_file_manager()  # get an s3 or local file manager
    player = config.get_player()    # get an alexa or pygame player
    audio_handler = AudioManager(player=player, storage_manager=storage_mgr, target_speed=speed, translator=translator)

    try:
        rows = verbs_db.query_dynamic_cards(page_size=page_size_num, offset=offset_num)
        if len(rows) == 0:
            session_attributes['deck'] = []
            session_attributes['state'] = "QUERY_COMPLETED"
            session_attributes['counter'] = 0
            return

        for flash_card in rows:
            print("%r" % flash_card.to_string())
            flash_card.set_destination(translator.target_language_code, translator.voice_id)
            audio_handler.insert_translation(flash_card=flash_card)
            session_attributes['offset'] += 1

        session_attributes['deck'] = audio_handler.deck
        session_attributes['state'] = "DECK_QUEUED"
        session_attributes['counter'] = 0

    except Exception as er:
        print("deal with this error")


def handle_start_request(request_string):
    pass


#
# start asking questions
# valid state = collecting
#
def start():
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

