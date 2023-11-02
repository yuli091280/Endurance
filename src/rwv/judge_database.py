import sqlite3


class JudgeDatabase:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)

    def __del__(self):
        self.connection.close()

    def executeLookupQuery(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()

        return result

    def singleQueryResult(queryResult):
        if queryResult:
            return queryResult[0]
        else:
            return None

    def judgeById(self, judge_id):
        result = self.executeLookupQuery(
            "SELECT * FROM Judge WHERE IDJudge = ?", (judge_id,)
        )
        return JudgeDatabase.singleQueryResult(result)

    def athleteByBib(self, bib_num):
        result = self.executeLookupQuery(
            "SELECT * FROM Athlete WHERE BibNumber = ?", (bib_num,)
        )
        return JudgeDatabase.singleQueryResult(result)

    def raceById(self, race_id):
        result = self.executeLookupQuery(
            "SELECT * FROM Race WHERE IDRace = ?", (race_id,)
        )
        return JudgeDatabase.singleQueryResult(result)

    def getJudgeCallData(self, race_id, bib_num):
        result = self.executeLookupQuery(
            "SELECT * FROM JudgeCall WHERE IDRace = ? AND BibNumber = ?",
            (race_id, bib_num),
        )
        return result
