from typing import List

import psycopg2

from source.configure import Configuration
from source.model import FlashCard


class Database(object):
    pronouns = {
        "i": ("pronoun_i", "valid_i"),
        "he": ("pronoun_he", "valid_he"),
        "she": ("pronoun_he", "valid_he"),
        "it": ("pronoun_he", "valid_he"),
        "you": ("pronoun_you", "valid_you"),
        "we": ("pronoun_we", "valid_we"),
        "they": ("pronoun_they", "valid_their"),
    }

    tenses = {
        "present": "present_tense",
        "past": "past_tense",
        "future": "future_tense",

    }

    _instance = None

    @staticmethod
    def get_instance():
        if Database._instance is None:
            c = Configuration.get_instance()
            Database._instance = Database(
                user=c.database_user,
                password=c.database_password,
                host=c.database_host,
                port=c.database_port,
                database=c.database)
        return Database._instance

    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        self.sql_statement = ""
        self.connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port="5432")

    def query_dynamic_cards(self, offset, page_size) -> List[FlashCard]:
        # 0=conjugation_id, 1=phrase_id, 2=verb, 3=tense, 4=pronoun, 5=conjugation,  6=phrase, rn
        limits = f""" limit {page_size} offset {offset}"""
        sql = self.sql_statement + limits
        print(f"QUERY: {limits}")
        cur = self.connection.cursor()
        cur.execute(sql)
        query_rows = cur.fetchall()
        response = []
        for row in query_rows:
            flashCard = FlashCard(
                conjugated=row[5],
                infinitive=row[2],
                tense=row[3],
                source_phrase=row[6],
                source_lang="en",
                conjugation_id=row[0],
                expression_id=row[1],
                pronoun=row[4])
            response.append(flashCard)
        return response

    def set_dynamic_cards_query(self, source_lang: str, pronouns: str = None, tenses: str = None, verbs: str = None, standard=False, distinct=True, random=False):

        pronoun_list = [] if not pronouns else list(map(lambda y: f"""'{y}'""", pronouns))
        tense_list = [] if not tenses else list(map(lambda y: f"""'{y}'""", tenses))
        verb_list = [] if not verbs else list(map(lambda y: f"""'{y}'""", verbs))
        where_list = []
        if standard:
            where_list.append("standard")  # include only one of each conjugation
        elif distinct:
            where_list.append("rn = 1")  # include only one of each conjugation
        if len(tense_list) > 0:
            s = ", ".join(tense_list)
            where_list.append(f"tense in ({s})")
        if len(pronoun_list) > 0:
            s = ", ".join(pronoun_list)
            where_list.append(f"pronoun in ({s})")
        if len(verb_list) > 0:
            s = ", ".join(verb_list)
            where_list.append(f"verb in ({s})")
        where_clause = "" if len(where_list) == 0 else "where " + " and ".join(where_list)
        order_clause = "" if random else " order by verb, T.ordinal, P.ordinal, rn "

        self.sql_statement = f"""select conjugation_id, phrase_id, verb, tense, pronoun, conjugation,  phrase, rn, standard
        from ( select C.conjugation_id,
                        R.phrase_id,
                        C.verb,
                        C.tense,
                        C.pronoun,
                        C.conjugation,
                        R.phrase,
                        R.standard,
                        row_number() over (partition by C.conjugation_id) as rn
                 from verbs.conjugations C
                          join verbs.pronouns P on P.pronoun = C.pronoun
                          join verbs.tenses T on T.tense = C.tense
                          join verbs.phrases R on R.verb = C.verb
            {order_clause}
             ) X {where_clause}"""


# if __name__ == "__main__":
#     db = Database(database="postgres", user="postgres", password="chinois1",
#                      host="aws-postgres-1.cxq7vuc4ekiv.us-east-1.rds.amazonaws.com", port="5432")
#     db.set_dynamic_cards_query(pronouns="i he or we", tenses="present and past", verbs="stay and have")
#
#     page_size_num = 25
#     offset_num = 0
#     for i in range(100):
#         rows = db.query_dynamic_cards(page_size=page_size_num, offset=offset_num)
#         if len(rows) == 0:
#             break
#         print("\n---fetch---")
#         for r in rows:
#             print("%r" % r.to_string())
#         offset_num += page_size_num
#
#     pass
