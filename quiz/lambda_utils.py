import json
import logging
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

personas = {
    "first": {"plural": "we", "singular": "i"},
    "second": {"plural": "you", "singular": "you"},
    "third": {"plural": "they", "singular": "he"}
}


class SlotInfo:

    @staticmethod
    def get_instance(slot, key, default):
        slot_arg = None
        if key in slot:
            slot_arg = slot[key]
        return SlotInfo(slot=slot_arg, default=default)

    def __init__(self, slot, default):
        logger.info("SLOT DATA V5: {}".format(slot))
        self.topic: str = slot.name
        self.utterance: str = slot.value
        self.resolved_values: List[str] = []
        if slot is not None and slot.resolutions is not None:
            resolutions = slot.resolutions
            resolutions_per_authority = None if not resolutions else resolutions.resolutions_per_authority
            for resolute in resolutions_per_authority:
                values = resolute.values
                if values is None:
                    logger.info("NO RESOLUTION VALUES IN {}".format(resolute))
                else:
                    # [{'value': {'id': '68e2d83709f317938b51e53f7552ed04', 'name': 'past'}}]
                    for value_item in values:
                        v = value_item.value
                        self.resolved_values.append(v.name)

        if len(self.resolved_values) == 0:
            logger.info("PARSE RESOLVED")
            if len(self.utterance) > 0:
                logger.info("PARSE UTTERANCE {}".format(self.utterance))
                if self.topic == "tense":
                    self.resolved_values = self.parse_tenses(self.utterance)
                elif self.topic == "game_type":
                    self.resolved_values = self.parse_tenses(self.utterance)
                elif self.topic == "person":
                    self.resolved_values = self.parse_personas(self.utterance)
                elif self.topic == "verbs":
                    self.resolved_values = self.parse_verbs(self.utterance)
                elif self.topic == "plurality":
                    self.resolved_values = self.parse_pluralities(self.utterance)
                else:
                    logger.info("CANNOT FIND {}".format(self.topic))
        elif self.utterance == "all" or self.resolved_values[0]=="all":
                if self.topic == "tense":
                    self.resolved_values = ["past", "present", "future"]
                elif self.topic == "person":
                    self.resolved_values = ["first", "second", "third"]
                elif self.topic == "verbs":
                    self.resolved_values = []
                elif self.topic == "plurality":
                    self.resolved_values = ["singular", "plural"]

        if len(self.resolved_values) == 0:
            self.resolved_values = default

    def parse_verbs(self, request_string: str) -> List[str]:
        words = request_string.split()
        logger.info("YES WE ARE PARSING VERBS: {}".format(",".join(words)))
        verbs = {}
        for i in range(len(words)):
            word = words[i]
            if (word == "to" or word.endswith("to")) and i + 1 < len(words):
                verbs[words[i + 1]] = i + 1
        return list(verbs.keys())

    def parse_personas(self, request_string: str) -> List[str]:
        v = request_string.replace("1st", "first").replace("2nd", "second").replace("3rd", "third")
        words = list(set(v.split()))
        return list(
            filter(lambda x: x in ("third", "first", "second"), words))

    def parse_pluralities(self, request_string: str) -> List[str]:
        words = request_string.split()
        return list(
            filter(lambda x: x in ("plural", "singular"), words))

    def parse_tenses(self, request_string: str) -> List[str]:
        words = request_string.split()
        return list(
                filter(lambda x: x in ("future", "past", "present"), words))

    def to_string(self):
        return json.dumps(self.__dict__)


def convert_person_to_pronouns(person: SlotInfo, plurality: SlotInfo):
    pronouns = set()
    for p in person.resolved_values:
        for s in plurality.resolved_values:
            if p in personas and s in personas[p]:
                pronouns.add(personas[p][s])
    return list(pronouns)
