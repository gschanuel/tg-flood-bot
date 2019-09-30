from settings import user, passwd, database
import mysql.connector
from mysql.connector import Error
import threading

some_lock = threading.Lock()
print("start")

class MySQL_DB:
    print("class")

    #"""Database interface"""
    def __init__(self):
        self.connect_mysql()
        pass

    def retry(func):
        print ("Retry")
        def wrapper(self, *args, **kwargs):
            with some_lock:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    print ("--->{}".format(e))
                    self.connect_mysql()
                else:
                    # No need to retry for other reasons
                    pass
                return func(self, *args, **kwargs)
        print("exit retry")
        return wrapper

    def connect_mysql(self):
        print ("connect")
        # do connection
        self.con = mysql.connector.connect(
                              #host='localhost',
                              unix_socket="/run/mysqld/mysqld.sock",
                              user=user,
                              passwd=passwd,
                              database=database,
                              use_unicode=True
        )
        if (self.con.is_connected()):
            self.cursor = self.con.cursor()
            self.cursor.execute("SET NAMES utf8mb4")
            self.cursor.execute("SET CHARACTER SET utf8mb4")
            self.cursor.execute("SET character_set_connection=utf8mb4")
            print("conectado")
        return self

    @retry
    def get_quote(self):
        print("[!][get_quote]")
        query = "SELECT text FROM lauters ORDER BY RAND() LIMIT 1"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        print("__{}__".format(row[0]))
    
    def __exit__(self):
        # do something
        if (self.con.is_connected()):
            self.cursor.close()
            self.con.close()
            print("Deu pau")
if __name__ == "__main__":
    import time
    db = MySQL_DB()
    db.get_quote()
    time.sleep(5)
    db.get_quote()
