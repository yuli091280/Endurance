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

    @staticmethod
    def single_query_result(query_result):
        if len(query_result) > 0:
            return query_result[0]
        else:
            return None

    def judge_by_id(self, judge_id):
        result = self.execute_lookup_query(
            "SELECT * FROM Judge WHERE IDJudge = ?", (judge_id,)
        )
        return DB.single_query_result(result)

    def athlete_by_bib(self, bib_num):
        result = self.execute_lookup_query(
            "SELECT * FROM Athlete A "
            "JOIN Bib B ON A.IDAthlete = B.IDAthlete "
            "WHERE B.BibNumber = ?",
            (bib_num,),
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

    def get_athletes_by_race_id(self, race_id):
        result = self.execute_lookup_query(
            "SELECT LastName, FirstName, BibNumber FROM Athlete A "
            "JOIN Bib B ON A.IDAthlete = B.IDAthlete WHERE IDRace = ? "
            "ORDER BY B.BibNumber",
            (race_id,),
        )
        return result

    # Queries for tables in the report
    def get_judge_infraction_summary(self):
        return self.execute_lookup_query(
            "SELECT FirstName, LastName,"
            "SUM(CASE WHEN Color = 'Red' AND Infraction = '~' THEN 1 ELSE 0 END) AS `Red ~`,"
            "SUM(CASE WHEN Color = 'Red' AND Infraction = '<' THEN 1 ELSE 0 END) AS `Red <`,"
            "SUM(CASE WHEN Color = 'Yellow' AND Infraction = '~' THEN 1 ELSE 0 END) AS 'Yellow ~',"
            "SUM(CASE WHEN Color = 'Yellow' AND Infraction = '<' THEN 1 ELSE 0 END) AS 'Yellow <' "
            "FROM Judge J "
            "JOIN JudgeCall JC ON J.IDJudge = JC.IDJudge "
            "GROUP by J.IDJudge "
            "ORDER BY J.FirstName, J.LastName",
            (),
        )

    def get_athlete_judge_infraction_summary(self):
        return self.execute_lookup_query(
            "SELECT B.BibNumber, A.FirstName , A.LastName, J.FirstName, J.LastName,"
            "(CASE WHEN Color = 'Yellow' AND Infraction = '~' THEN 'x' ELSE NULL END) AS `Yellow ~`,"
            "(CASE WHEN Color = 'Red' AND Infraction = '~' THEN 'x' ELSE NULL END) AS `Red ~`,"
            "(CASE WHEN Color = 'Yellow' AND Infraction = '<' THEN 'x' ELSE NULL END) AS `Yellow <`,"
            "(CASE WHEN Color = 'Red' AND Infraction = '<' THEN 'x' ELSE NULL END) AS `Red <` "
            "FROM Judge J "
            "JOIN JudgeCall JC ON J.IDJudge = JC.IDJudge "
            "JOIN Bib B ON JC.BibNumber = B.BibNumber "
            "JOIN Athlete A ON B.IDAthlete = A.IDAthlete "
            "GROUP BY A.IDAthlete, J.IDJudge "
            "ORDER BY B.BibNumber, J.FirstName, J.LastName",
            (),
        )

    def get_athlete_infraction_summary(self):
        return self.execute_lookup_query(
            "SELECT B.BibNumber, A.FirstName AS 'Athlete First Name', A.LastName AS 'Athlete First Name',"
            "SUM(CASE WHEN Color = 'Yellow' AND Infraction = '~' THEN 1 ELSE 0 END) AS `Yellow ~`,"
            "SUM(CASE WHEN Color = 'Yellow' AND Infraction = '<' THEN 1 ELSE 0 END) AS `Yellow <`,"
            "SUM(CASE WHEN Color = 'Red' AND Infraction = '~' THEN 1 ELSE 0 END) AS `Red ~`,"
            "SUM(CASE WHEN Color = 'Red' AND Infraction = '<' THEN 1 ELSE 0 END) AS `Red <` "
            "FROM JudgeCall JC "
            "JOIN Bib B ON JC.BibNumber = B.BibNumber "
            "JOIN Athlete A ON B.IDAthlete = A.IDAthlete "
            "GROUP BY A.IDAthlete "
            "ORDER BY B.BibNumber ",
            (),
        )

    def get_red_without_yellow_summary(self):
        return self.execute_lookup_query(
            "SELECT FirstName, LastName,"
            "        SUM(CASE WHEN Color = 'Red' AND Infraction = '~' AND NOT EXISTS ("
            "                SELECT * FROM JudgeCall J2"
            "                WHERE J1.IDJudge = J2.IDJudge AND J1.IDRace = J2.IDRace AND J1.BibNumber = J2.BibNumber AND J2.Infraction = '~' AND J2.Color = 'Yellow' AND J2.TOD < J1.TOD LIMIT 1)"
            "        THEN 1 ELSE 0 END) AS `# of ~ Red cards without Yellow`,"
            "        SUM(CASE WHEN Color = 'Red' AND Infraction = '<' AND NOT EXISTS ("
            "                SELECT * FROM JudgeCall J2"
            "                WHERE J1.IDJudge = J2.IDJudge AND J1.IDRace = J2.IDRace AND J1.BibNumber = J2.BibNumber AND J2.Infraction = '<' AND J2.Color = 'Yellow' AND J2.TOD < J1.TOD LIMIT 1)"
            "        THEN 1 ELSE 0 END) AS `# of < Red cards without Yellow` "
            "FROM JudgeCall J1 "
            "JOIN Judge J ON J1.IDJudge = J.IDJudge "
            "Group By J1.IDJudge "
            "Order By FirstName, LastName",
            (),
        )

    def get_yellow_without_red_summary(self):
        return self.execute_lookup_query(
            "SELECT FirstName, LastName,"
            "        SUM(CASE WHEN Color = 'Yellow' AND Infraction = '~' AND NOT EXISTS ("
            "                SELECT * FROM JudgeCall J2"
            "                WHERE J1.IDJudge = J2.IDJudge AND J1.IDRace = J2.IDRace AND J1.BibNumber = J2.BibNumber AND J2.Infraction = '~' AND J2.Color = 'Red' AND J1.TOD < J2.TOD LIMIT 1)"
            "        THEN 1 ELSE 0 END) AS `# of ~ Yellow not followed by a Red`,"
            "        SUM(CASE WHEN Color = 'Yellow' AND Infraction = '<' AND NOT EXISTS ("
            "                SELECT * FROM JudgeCall J2"
            "                WHERE J1.IDJudge = J2.IDJudge AND J1.IDRace = J2.IDRace AND J1.BibNumber = J2.BibNumber AND J2.Infraction = '<' AND J2.Color = 'Red' AND J1.TOD < J2.TOD LIMIT 1)"
            "        THEN 1 ELSE 0 END) AS `# of < Yellow not followed by a Red` "
            "FROM JudgeCall J1 "
            "JOIN Judge J ON J1.IDJudge = J.IDJudge "
            "Group By J1.IDJudge "
            "Order By FirstName, LastName",
            (),
        )

    def get_judge_consistency_report(self):
        # todo: write the sql query
        return None

    def get_per_athlete_calls_summary(self):
        return self.execute_lookup_query(
            "SELECT B.BibNumber, A.FirstName AS 'Athlete First Name', A.LastName AS 'Athlete First Name',"
            "SUM(CASE WHEN Color = 'Yellow' THEN 1 ELSE 0 END) AS '# of Yellow Paddles',"
            "SUM(CASE WHEN Color = 'Red' THEN 1 ELSE 0 END) AS '# of Red Cards' "
            "FROM JudgeCall JC "
            "JOIN Bib B ON JC.BibNumber = B.BibNumber "
            "JOIN Athlete A ON B.IDAthlete = A.IDAthlete "
            "GROUP BY A.IDAthlete "
            "ORDER BY B.BibNumber",
            (),
        )

    def get_loc_values_by_race_id(self, race_id):
        return self.execute_lookup_query(
            "SELECT BibNumber, LOCAverage, TOD as Time FROM VideoObservation WHERE IDRace = ? ORDER BY "
            "BibNumber, TOD",
            (race_id,),
        )

    def get_judge_data_by_race_id(self, race_id):
        return self.execute_lookup_query(
            "SELECT TOD AS Time, IDJudge, BibNumber, Infraction, Color FROM JudgeCall WHERE IDRace = ? ORDER BY "
            "BibNumber, TOD",
            (race_id,),
        )
