import sqlite3

class JudgeDatabase:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)

    def __del__(self):
        self.connection.close()


    def judgeById(self, judge_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Judge WHERE IDJudge = ?", (judge_id,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return result[0]
        else:
            return None


    def athleteByBib(self, bib_num):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Athlete WHERE BibNumber = ?", (bib_num,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return result[0]
        else:
            return None


    def raceById(self, race_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Race WHERE IDRace = ?", (race_id,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return result[0]
        else:
            return None

def main():
    db_path='test.db'  
    db = JudgeDatabase(db_path)
    judge_id=1  
    name = db.findJudgeName(judge_id)
    print(name)

if __name__ == "__main__":
    main()

