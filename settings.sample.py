import mysql.connector
TOKEN = '**********'
msg_flood = 5
msg_interval = 20
botName = "botDev"
con = mysql.connector.connect(
        host="localhost", 
        user="db_user", 
        passwd="**********",
        database="db_telegram",
        use_unicode=True
        )
cursor = con.cursor()
cursor.execute('SET NAMES utf8mb4')
cursor.execute("SET CHARACTER SET utf8mb4")
cursor.execute("SET character_set_connection=utf8mb4")
