import sqlite3

class JudgeDatabase:
    def __init__(self, db_path):
        self.db_path = db_path #set db 


    def createJudgeTable(self):
        connection = sqlite3.connect(self.db_path) #connection
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE JUDGETABLE...")
        cursor.close()


    def findJudgeName(self, judge_id):
        connection = sqlite3.connect(self.db_path) #connection
        cursor = connection.cursor()

        #sql query, the judges table would work if we have another another function where a table is created with the name "JudgeTable". 
        #self.createJudgeTable()
        cursor.execute("SELECT name FROM JudgeTable WHERE id = ?", (judge_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close() #disconnect
        
        if result:
            return result[0] #
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

