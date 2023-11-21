import sqlite3


class DB:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)

    def __del__(self):
        self.connection.close()

    def execute_lookup_query(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()

        return result

    def single_query_result(queryResult):
        if len(queryResult) > 0:
            return queryResult[0]
        else:
            return None

    def judge_by_id(self, judge_id):
        result = self.execute_lookup_query(
            "SELECT * FROM Judge WHERE IDJudge = ?", (judge_id,)
        )
        return DB.single_query_result(result)

    def athlete_by_bib(self, bib_num):
        result = self.execute_lookup_query(
            "SELECT * FROM Athlete WHERE BibNumber = ?", (bib_num,)
        )
        return DB.single_query_result(result)

    def race_by_id(self, race_id):
        result = self.execute_lookup_query(
            "SELECT * FROM Race WHERE IDRace = ?", (race_id,)
        )
        return DB.single_query_result(result)

    def get_judge_call_data(self, race_id, bib_num):
        result = self.execute_lookup_query(
            "SELECT * FROM JudgeCall WHERE IDRace = ? AND BibNumber = ?",
            (race_id, bib_num),
        )
        return result
