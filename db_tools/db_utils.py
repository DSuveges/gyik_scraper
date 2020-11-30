import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger('__main__')


class db_handler(object):
    """
    This class defines the modules to add data directly to the database.
    Contains all the SQL statements as well.
    """


    # Add new user to table:
    add_user_sql = '''INSERT INTO USER(USER, USER_PERCENT)
                    VALUES(:user, :user_percent)'''

    # Update percent of an existing user:
    update_percent_sql = '''UPDATE USER
                    SET USER_PERCENT = :user_percent
                    WHERE USER = :user'''

    # Retrieve user based on username:
    get_user_sql = '''SELECT * FROM USER WHERE USER = :user'''

    # Retrieve keyword:
    get_keyword_sql = '''SELECT * FROM KEYWORD WHERE KEYWORD = :keyword'''

    # Add keyword:
    add_keyword_sql = '''INSERT INTO KEYWORD(KEYWORD) VALUES(:keyword)'''

    # Look up question in the database based on the gyik id:
    question_lookup_sql = '''SELECT * FROM QUESTION WHERE GYIK_ID = :gyik_id'''

    # Look up study in the database based on the gyik id:
    link_to_keyword_sql = '''INSERT INTO QUESTION_KEYWORD (QUESTION_ID, KEYWORD_ID)
                    VALUES(:question_id, :keyword_id)'''

    # Test keyword linking:
    get_link_sql = '''SELECT * FROM QUESTION_KEYWORD
                WHERE QUESTION_ID = :question_id
                AND KEYWORD_ID = :keyword_id'''

    # Add question to database:
    add_question_sql = '''INSERT INTO QUESTION(
                GYIK_ID, CATEGORY, SUBCATEGORY,
                QUESTION_TITLE, QUESTION,
                QUESTION_DATE, URL, USER_ID, ADDED_DATE)
        VALUES(:gyik_id, :category, :subcategory,
            :question_title, :question,
            :question_date, :url, :user_id, :added_date)'''

    # Look up an answer in the database based on the gyik id:
    get_answer_sql = '''SELECT * FROM ANSWER WHERE GYIK_ID = :gyik_id'''

    # Inserting data to answers:
    add_answer_sql = '''INSERT INTO ANSWER(
                GYIK_ID, USER_ID, QUESTION_ID,
                ANSWER_DATE, ANSWER_TEXT,
                USER_PERCENT, ANSWER_PERCENT)
        VALUES(:gyik_id, :user_id, :question_id,
            :answer_date, :answer_text,
            :user_percent, :answer_percent)'''

    def __init__(self, connection):
        """
        To initialize the db handler object,
        """

        if not isinstance(connection, sqlite3.Connection):
            raise TypeError ("Connection object is expected for initialize add_data object.")

        self.conn = connection
        self.cursor = connection.cursor()

    def link_to_keyword(self, question_id, keyword_id):
        """
        Linking question to keyword
        """

        # Does the link exists?
        self.cursor.execute(self.get_link_sql, {'question_id' : question_id, 'keyword_id' : keyword_id})

        # Add link if not yet in the database:
        if not self.cursor.fetchone():
            self.cursor.execute(self.link_to_keyword_sql, {'question_id' : question_id, 'keyword_id' : keyword_id})
        else:
            logger.warning('Question/keyword link already exist.')

    def add_user(self,user,percent):
        '''
        Get user ID or adds to db. Also updates percent if
        missing in db, but in the query
        '''

        # Fetch data from db:
        self.cursor.execute(self.get_user_sql, {'user' : user})

        # The user is in the database:
        try:
            # Parsing row:
            (ID,USER,USER_PERCENT) = self.cursor.fetchone()

            # If percent is missing, let's update:
            if percent and not USER_PERCENT:
                self.cursor.execute(self.update_percent_sql, {'user' : user, 'user_percent' : percent})

        # If user is not in the database we add it:
        except TypeError:
            self.cursor.execute(self.add_user_sql, {'user' : user, 'user_percent' : percent})
            ID = self.cursor.lastrowid

        # Return with the ID
        return ID

    def add_keyword(self, keyword):
        """
        Testing if keyword exists. If no, adds to database.
        Returns keyword ID.
        """

        # None values cannot be added:
        if not keyword:
            logger.warning('Keyword must be specified!')
            return None

        # Fetch data from db:
        self.cursor.execute(self.get_keyword_sql, {'keyword' : keyword})

        # The user is in the database:
        try:
            # Parsing row:
            (ID,KEYWORD) = self.cursor.fetchone()

        # If user is not in the database we add it:
        except TypeError:
            self.cursor.execute(self.add_keyword_sql, {'keyword' : keyword})
            ID = self.cursor.lastrowid

        # Return with the ID
        return ID

    def test_question(self, gyik_id):
        """
        Based on gyik ID of the question, we tests if it is already in the database:
        """

        # Fetch data from db:
        self.cursor.execute(self.question_lookup_sql, {'gyik_id' : gyik_id})

        # The question is in the database:
        if self.cursor.fetchone():
            return 1
        else:
            return 0

    def add_question(self, question_data):
        """
        This methods adds a new row to the question data
        """

        # Test if data is in a proper type:
        if not isinstance(question_data, dict):
            raise TypeError ('Question data must be a dictionary')

        # Test if all required values exist:
        for field in ['URL','GYIK_ID','TITLE','CATEGORY','SUBCATEGORY','QUESTION','QUESTION_DATE','USER_ID']:
            if field not in question_data:
                raise KeyError ('Question data must contain key: {}'.format(field))

        # Test if this question is already in the database:
        if self.test_question(question_data['GYIK_ID']):
            logger.warning(f'This question id ({question_data["GYIK_ID"]}) has already been added to the database! Skipping')
            return None

        # Submit query:
        d = {
                'gyik_id' : question_data['GYIK_ID'],
                'category' : question_data['CATEGORY'],
                'subcategory' : question_data['SUBCATEGORY'],
                'question_title' : question_data['TITLE'],
                'question' : question_data['QUESTION'],
                'question_date' : question_data['QUESTION_DATE'],
                'url' : question_data['URL'],
                'user_id' : question_data['USER_ID'],
                'added_date' : datetime.now()
            }
        self.cursor.execute(self.add_question_sql, d)

        return self.cursor.lastrowid

    def test_answer(self, gyik_id):
        """
        Test if the gyik ID of the answer exist
        """

        # Fetch data from db:
        self.cursor.execute(self.get_answer_sql, {'gyik_id' : gyik_id})

        # The question is in the database:
        if self.cursor.fetchone():
            return 1
        else:
            return 0

    def add_answer(self, answer_data):
        """
        This methods adds a new row to the question data
        """

        # Test input data:
        if not isinstance(answer_data, dict):
            raise TypeError ('Answer data must be a dictionary')

        # Test if all required values exist:
        for field in ['USER_ID','GYIK_ID','ANSWER_DATE','ANSWER_TEXT','ANSWER_PERCENT','USER_PERCENT']:
            if field not in answer_data:
                raise KeyError ('Answer data must contain key: {}'.format(field))

        # Test if this question is already in the database:
        if self.test_answer(answer_data['GYIK_ID']):
            logger.warning(f'This question ({answer_data["GYIK_ID"]}) has already been added to the database! Skipping')
            return None

        # Submit query:
        d = {
                'gyik_id' : answer_data['GYIK_ID'],
                'answer_date' : answer_data['ANSWER_DATE'],
                'answer_text' : answer_data['ANSWER_TEXT'],
                'user_percent' : answer_data['USER_PERCENT'],
                'answer_percent' : answer_data['ANSWER_PERCENT'],
                'question_id' : answer_data['QUESTION_ID'],
                'user_id' : answer_data['USER_ID']
            }
        self.cursor.execute(self.add_answer_sql, d)

        return self.cursor.lastrowid

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

class question_loader(object):
    """
    This class loads data of a full question (question, keywords, answers etc) into the database.
    There is a very specific order in which the data can be loaded into the database.
    """

    def __init__(self,db_handler):
        """
        Initialize object with db_handler. When data is subsequently added, this handler
        is going to be called.
        """

        # Storing db_handler:
        self.db_obj = db_handler

    def add_question(self,question_data):
        """
        Once all components of the question is parsed and the proper data structure built,
        we upload the data.
        """

        # 1. Adding user - person who asked the question is often not available. If yes, we add to the db.
        if not question_data['USER']['USER']:
            question_data['USER_ID'] = None
        else:
            question_data['USER_ID'] = self.db_obj.add_user(question_data['USER']['USER'],
                                                            question_data['USER']['USER_PERCENT'])

        # 2. Add question
        question_id = self.db_obj.add_question(question_data)

        # If question is already in the database, return
        if not question_id:
            return

        # Loop through all keywords:
        for keyword in question_data['KEYWORDS']:

            # 3. Add keywords
            keyword_id = self.db_obj.add_keyword(keyword)

            # 4. Add links to keywords
            self.db_obj.link_to_keyword(question_id,keyword_id)

        # Loop through all answers:
        for answer in question_data['ANSWERS']:
            answer['QUESTION_ID'] = question_id
            # 6. Add users
            if answer['USER']['USER']:
                answer['USER_ID'] = self.db_obj.add_user(answer['USER']['USER'],
                                                    answer['USER']['USER_PERCENT'])
            else:
                answer['USER_ID'] = None

            # 5. Add answers
            self.db_obj.add_answer(answer)

        # The changes are only committed after all uploads were successfully completed.
        self.db_obj.commit()

        