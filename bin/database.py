
import sqlite3

databaseName = 'users.db'
class DataBase():
    def __init__(self):
        self.conn = sqlite3.connect(databaseName)
        self.cursor = self.conn.cursor()
        try:
            self.get_dataframe()

        except Exception as E:
            self.create_table()


    def create_table(self):
        try:
            self.cursor.execute("CREATE TABLE rating (user text, rating text, lastJoinDate boolean)")
        except:
            pass

    def get_dataframe(self, *args, **kwargs):
        # return iterator of all table's data
        rowsUsers = self.cursor.execute("SELECT rowid, * FROM rating ORDER BY user")
        return self.cursor.fetchall()

    def get_user(self,*args, **data):
        username = data['username']
        # return user data by username
        sql = "SELECT * FROM rating WHERE user=?"
        self.cursor.execute(sql, [(username)])
        return self.cursor.fetchall()


    def append_user(self, *args, **data):
        username = data['username']

        rating = 0
        date = data['date']
        self.cursor.execute("INSERT INTO rating (user, rating, lastJoinDate) VALUES (?, ?, ?)",
                            (username, 0, date))
        self.conn.commit()

    def user_commit(self, *args, **data):
        username = data['username']
        rating = data['rating']
        date = data['date']
        self.cursor.execute("UPDATE rating SET rating=?, lastJoinDate=? WHERE user=?",
                            (rating, date, username)
                           )
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.conn.close()