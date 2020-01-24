import sqlite3
import datetime
import pickle

class db_connection(object):

    # The table in which the potential keywords are stored for a question:
    keyword_table_sql = """CREATE TABLE IF NOT EXISTS KEYWORD (
        ID INTEGER PRIMARY KEY,
        KEYWORD TEXT NOT NULL
    )"""
    
    # Table with all the user information is available:
    user_table_sql = """CREATE TABLE IF NOT EXISTS USER (
        ID INTEGER PRIMARY KEY,
        USER TEXT NOT NULL,
        USER_PERCENT NUMERIC
    )"""

    # Table in which we store question data:
    question_table_sql = """CREATE TABLE IF NOT EXISTS QUESTION (
        ID INTEGER PRIMARY KEY,
        GYIK_ID INTEGER NOT NULL,
        CATEGORY TEXT NOT NULL,
        SUBCATEGORY TEXT NOT NULL,
        QUESTION_TITLE TEXT NOT NULL,
        QUESTION TEXT,
        QUESTION_DATE DATETIME NOT NULL,
        URL TEXT NOT NULL,
        USER_ID INTEGER,
        ADDED_DATE DATETIME NOT NULL,
        FOREIGN KEY (USER_ID) REFERENCES USER (ID) 
    )"""

    # Table with the answers:
    answer_table_sql = """CREATE TABLE IF NOT EXISTS ANSWER (
        ID INTEGER PRIMARY KEY,
        USER_ID INTEGER,
        GYIK_ID INTEGER NOT NULL, 
        QUESTION_ID INTEGER NOT NULL,
        ANSWER_DATE DATETIME NOT NULL,
        ANSWER_TEXT TEXT NOT NULL,
        USER_PERCENT NUMERIC,
        ANSWER_PERCENT NUMERIC,
        FOREIGN KEY (USER_ID) REFERENCES USER (ID),
        FOREIGN KEY (QUESTION_ID) REFERENCES QUESTION (ID)
    )"""

    # Linking table making connection between questions and keywords:
    question_keyword_table_sql = """CREATE TABLE IF NOT EXISTS QUESTION_KEYWORD (
        KEYWORD_ID INTEGER NOT NULL,
        QUESTION_ID INTEGER NOT NULL,
        FOREIGN KEY (KEYWORD_ID) REFERENCES KEYWORD (ID),
        FOREIGN KEY (QUESTION_ID) REFERENCES QUESTION (ID)    
    )"""
    
    
    def __init__(self, filename):
        # Create connection:
        self._create_connection(filename)
        
        # Create all tables:
        self._create_all_tables()
        
        
    def _create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
            self.conn = None
    
    def _create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
            
    def _create_all_tables(self):
        tables_to_create = ['keyword','user','question','answer','question_keyword']
        
        # create all tables
        if self.conn is not None:
            for table in tables_to_create:
                print('[Info] Creating {}'.format(table))
                sql_statement = getattr(self, table+'_table_sql')
                self._create_table(sql_statement)
        else:
            print("Error! cannot create the database connection.")

