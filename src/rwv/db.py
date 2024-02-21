import sqlite3


class DB:
    """
    Class that handles retrieving data from the SQLite database

    :param db_path: Path to the database file.
    :type db_path: str
    """

    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)

    def __del__(self):
        self.connection.close()

    def execute_lookup_query(self, query, params):
        """
        Executes the sql query

        :param query: sql query to run.
        :type query: str
        :param params: parameter to pass to sql query..
        :type params: list[any]
        :return: Data returned from sql query.
        :rtype: list[tuple[any]]
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()

        return result

    @staticmethod
    def single_query_result(query_result):
        """
        Filters a given sql query result for only the first item

        :param query_result: The SQL query result to filter
        :type query_result: str
        :return: Filtered result.
        :rtype: tuple[any]
        """
        if len(query_result) > 0:
            return query_result[0]
        else:
            return None

    def judge_by_id(self, judge_id):
        """
        Query this database for information on a particular judge

        :param judge_id: Id of the judge
        :type judge_id: int
        :return: Judge based on id.
        :rtype: list[tuple[any]]
        """
        result = self.execute_lookup_query(
            "SELECT * FROM Judge WHERE IDJudge = ?", (judge_id,)
        )
        return DB.single_query_result(result)

    def get_athlete_by_race_and_bib(self, race_id, bib_num):
        """Query this database for athlete information matching the given race id and bib number

        :param race_id: race id for this query
        :type race_id: int
        :param bib_num: bib number for this query
        :type bib_num: int

        :returns: a list of athlete information, each athlete will have their information in a tuple
        :rtype: list[tuple[any]]
        """
        result = self.execute_lookup_query(
            "SELECT * FROM Athlete A "
            "JOIN Bib B ON A.IDAthlete = B.IDAthlete "
            "WHERE B.BibNumber = ? AND B.IDRace = ?",
            (bib_num, race_id),
        )
        return DB.single_query_result(result)

    def race_by_id(self, race_id):
        """
        Returns race based on race id.

        :param race_id: race id
        :type race_id: int
        :return: Race based on race id.
        :rtype: tuple[any]
        """
        result = self.execute_lookup_query(
            "SELECT * FROM Race WHERE IDRace = ?", (race_id,)
        )
        return DB.single_query_result(result)

    def get_judge_call_data(self, race_id, bib_num):
        """
        Returns judge calls for a particular race and bib number

        :param race_id: race id
        :type race_id: int
        :param bib_num: bib number
        :type bib_num: int
        :return: Judge call data based on ID and Bib Number
        :rtype: list[tuple[any]]
        """
        result = self.execute_lookup_query(
            "SELECT * FROM JudgeCall WHERE IDRace = ? AND BibNumber = ?",
            (race_id, bib_num),
        )
        return result

    # Queries for tables in the report
    def get_judge_infraction_summary(self):
        """
        Judge infraction data.

        :return: Judge infraction data.
        :rtype: list[tuple[any]]
        """
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
        """
        Judge/Athlete infraction data.

        :return: Judge/Athlete infraction data.
        :rtype: list[tuple[any]]
        """
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
        """
        Athlete infraction data.

        :return: Athlete infraction data.
        :rtype: list[tuple[any]]
        """
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
        """
        Get data where there is a red card but no yellow card.

        :return: Data where there is a red card but no yellow card.
        :rtype: list[tuple[any]]
        """
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
        """
        Get data where there is a yellow card but no red card.

        :return: Data where there is a yellow card but no red card.
        :rtype: list[tuple[any]]
        """
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
        """
        Get data per athlete call.

        :return: Data per athlete call.
        :rtype: list[tuple[any]]
        """
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

    def get_bibs_by_race(self, race_id):
        """Query this database for all bib numbers of a race.

        :param race_id: Race id for this query.
        :type race_id: int

        :returns: A list of bib numbers.
        """
        return self.execute_lookup_query(
            "SELECT DISTINCT BibNumber FROM VideoObservation "
            "WHERE IDRace = ? AND LOCAverage IS NOT NULL",
            (race_id,),
        )

    def get_loc_by_race_and_bib(self, race_id, bib_num):
        """Query this database for LOC information matching the given race id and bib number.

        :param race_id: Race id for this query.
        :type race_id: int
        :param bib_num: Bib number for this query.
        :type bib_num: str

        :returns: A list of LOC information in the database, each instance is a tuple of (LOC value, Time of day).
        """
        return self.execute_lookup_query(
            "SELECT LOCAverage, TOD as Time FROM VideoObservation "
            "WHERE IDRace = ? AND BibNumber = ? AND LOCAverage IS NOT NULL",
            (race_id, bib_num),
        )

    def get_judge_data_by_race_and_bib(self, race_id, bib_num):
        """Query this database for judge data matching the given race id and bib number.

        :param race_id: Race id for this query.
        :type race_id: int
        :param bib_num: Bib number for this query.
        :type bib_num: str

        :returns: A list of judge data in the database, each instance is a tuple of (Time, IDJudge, Infraction, Color).
        :rtype: list[tuple[any]]
        """
        return self.execute_lookup_query(
            "SELECT TOD AS Time, IDJudge, Infraction, Color FROM JudgeCall "
            "WHERE IDRace = ? AND BibNumber = ?",
            (race_id, bib_num),
        )

    def get_judge_by_race(self, race_id):
        """Query this database for judges involved in a given race.

        :param race_id: Id of the race to get judge ids for.
        :type race_id: int

        :returns: A list of tuple, where each tuple contains information for a particular judge
        :rtype: list[tuple[any]]
        """
        return self.execute_lookup_query(
            "SELECT Judge.* FROM Judge "
            "JOIN JudgeCall ON Judge.IDJudge = JudgeCall.IDJudge "
            "WHERE JudgeCall.IDRace = ? GROUP BY Judge.IDJudge",
            (race_id,),
        )

    def get_races(self):
        """Query this database for all races.

        :returns: A list of race data, each instance is a tuple of (IDRace, Gender, Distance, DistanceUnits, RaceDate, StartTime).
        :rtype: list[tuple[any]]
        """
        return self.execute_lookup_query(
            "SELECT IDRace, Gender, Distance, DistanceUnits, RaceDate, StartTime FROM Race ORDER BY IDRace",
            (),
        )

    def get_judge_call_filtered(self, bib, race_id, judge_id, color, infraction):
        """Query this database for judge calls for use in filtering judge calls on the graph

        :param bib: Bib number of the athlete that the call was made against.
        :type bib: int
        :param race_id: The race where the call took place.
        :type race_id: int
        :param judge_id: Id of the judge who made the call.
        :type judge_id: int
        :param color: Color of the judge call.
        :type color: str
        :param infraction: Infraction that was called
        :type infraction: str
        """
        return self.execute_lookup_query(
            "SELECT TOD FROM JudgeCall "
            "WHERE BibNumber = ? AND IDRace = ? AND IDJudge = ? AND Color = ? AND Infraction = ?",
            (bib, race_id, judge_id, color, infraction),
        )
