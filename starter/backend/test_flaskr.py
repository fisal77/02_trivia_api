import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('caryn', 'caryn', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question":  "Heres a new question string",
            "answer":  "Heres a new answer string",
            "difficulty": 3,
            "category": 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    # change 'categories' key to test if failed
    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # change 'page' arg from 1000 to 2 to test if failed
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # change 'searchTerm' json value from 'boxer' to any word is not exist in database to test if failed
    def test_get_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'boxer'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']), 1)  # Also change the expected search result length

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'ttttttt'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        # self.assertEqual(data['success'], True)
        # self.assertTrue(data['categories'])
        # self.assertTrue(data['current_category'])
        # self.assertTrue(data['total_questions'])
        # self.assertTrue(len(data['questions']), 0)

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()