import sqlite3

# todo: move sqlite to backend file, handle abstract data here

class Model:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def database(self):
        self.conn = sqlite3.connect('pythontut.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS `member` (mem_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, firstname TEXT, lastname TEXT)")

    def create(self, first_name, last_name):
        self.database()
        self.cursor.execute("INSERT INTO `member` (firstname, lastname) VALUES(?, ?)", (str(first_name.get()), str(last_name.get())))
        self.cursor.execute("SELECT * FROM `member` ORDER BY `lastname` ASC")
        fetch = self.cursor.fetchall()
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        return fetch

    def read(self):
        self.database()
        self.cursor.execute("SELECT * FROM `member` ORDER BY `lastname` ASC")
        fetch = self.cursor.fetchall()
        self.cursor.close()
        self.conn.close()
        return fetch

    def update(self, member_id, first_name, last_name):
        self.database()
        self.cursor.execute("UPDATE `member` SET `firstname` = ?, `lastname` = ? WHERE `mem_id` = ?", (str(first_name.get()), str(last_name.get()), int(member_id.get())))
        self.conn.commit()
        self.cursor.execute("SELECT * FROM `member` ORDER BY `lastname` ASC")
        fetch = self.cursor.fetchall()
        self.cursor.close()
        self.conn.close()
        return fetch

    def delete(self, member_id):
        self.database()
        self.cursor.execute("DELETE FROM `member` WHERE `mem_id` = %d" % member_id)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
