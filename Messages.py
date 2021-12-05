import datetime
import json
import mysql.connector

with open("./storage/mysql_config.json") as f:
    config = json.load(f)

    host = config["host"]
    user = config["user"]
    password = config["password"]
    database = config["database"]


class Message():
    def __init__(self, author: str, url: str, image_url: str, reactions: int, posted_at: datetime.datetime):
        self.author = author
        self.url = url
        self.image_url = image_url
        self.reactions = reactions
        self.posted_at = posted_at


    def save(self):
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = connection.cursor()

        ignore_query = "SET SESSION SQL_MODE='ALLOW_INVALID_DATES';"
        cursor.execute(ignore_query)

        check_query = "SELECT * FROM memes WHERE url = %s"
        cursor.execute(check_query, (self.url,))

        if cursor.fetchone() is None:
            add_query = "INSERT INTO memes (author, url, image_url, reactions, posted_at) VALUES (%s, %s, %s, %s, %s)"
            values = (self.author, self.url, self.image_url, self.reactions, self.posted_at)
            cursor.execute(add_query, values)

            connection.commit()
            connection.close()