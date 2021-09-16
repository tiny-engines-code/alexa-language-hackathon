from typing import List

import mysql.connector as mysql

db = mysql.connect(
    host="localhost",
    user="clomeli",
    passwd="Blackphillip=1"
)


class Database(object):
    def __init__(self):
        self.db = mysql.connect(
            host="localhost",
            user="clomeli",
            passwd="chinois1"
        )


class VerbData(object):

    pronouns = {
        "i":  ("first_person", "valid_i"),
        "he":  ("third_person", None),
        "she":  ("third_person", None),
        "it":  ("third_person", None),
        "you":  ("first_person", "valid_you"),
        "we":  ("first_person", "valid_we"),
        "they":  ("first_person", "valid_their"),
    }
    
    tenses = {
        "present": "present_tense",
        "past": "past_tense",
        "future": "future_tense",
    
    }

    def __init__(self):
        pass
    
    def create_query(self, pronouns: List[str], tenses: List[str]):
        unions: List[str] = []
        for pronoun in pronouns:
            for tense in tenses:
                pronoun = pronoun.title()
                person = VerbData.pronouns[pronoun.lower()][0]
                validation_fld = VerbData.pronouns[pronoun.lower()][1]
                tense_field = self.tenses[tense]
                validation_clause = ""
                if validation_fld:
                    validation_clause = f" and E.{validation_fld} "
                sql =  f"""select concat('{pronoun} ', {person}, ' ', E.phrase) as phrase, C.conjugation_id, E.expression_id
                    from verbs.conjugations C join verbs.expressions E on E.verb = C.verb
                    where tense = '{tense}' and E.{tense_field}{validation_clause} order by C.verb"""
                unions.append(sql)
                    
        union_string = '\nunion distinct\n'.join(unions)
        return union_string
    
    
if __name__ == "__main__":
    verbs = VerbData()
    sql = verbs.create_query(["we"], ["future", "past"])
    print(sql)
    pass