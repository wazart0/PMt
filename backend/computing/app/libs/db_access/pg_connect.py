import psycopg2
from sqlalchemy import create_engine



class PGconnection():

    def __init__(self, host, user, password, database):
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        self.con = psycopg2.connect(host=self.host, user=self.user, password=self.password, database=self.database)
        return con.cursor()

    def disconnect(self):
        self.con.close()

    def get_engine(self):
        return create_engine('postgresql://' + self.user + ':' + self.password + '@' + self.host + ':5432/' + self.database)

