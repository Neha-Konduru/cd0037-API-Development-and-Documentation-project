import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('konduruneha@localhost:5432', self.database_name)
        self.app = create_app(test_config={'SQLALCHEMY_DATABASE_URI': self.database_path,'SQLALCHEMY_TRACK_MODIFICATIONS': False})
        self.client = self.app.test_client

        # binds the app to the current context
        with self.app.app_context():
            setup_db(self.app,self.database_path)
            # create all tables
            db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        response = self.client().post('/questions/search', json={'searchTerm':'Art'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertIsNotNone(data['total_questions'])
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])

    def test_search_questions_pagination_failure(self):
        response = self.client().post('/questions/search', json={'searchTerm': None})
        self.assertEqual(response.status_code, 422)

        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertTrue('error' in data)
        self.assertTrue('message' in data)
    
    def test_get_categories(self):
        response = self.client().get('/categories')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue('categories' in data)

        categories = data['categories']
        self.assertTrue(categories)

    def test_get_categories_failure(self):
        response = self.client().post('/categories')
        self.assertEqual(response.status_code, 405)

    def test_get_questions(self):
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue('categories' in data)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_failure(self):
        response = self.client().put('/questions')
        self.assertEqual(response.status_code, 405)

    def test_delete_question(self):
        response = self.client().delete('/questions/13')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_question_failure(self):
        response = self.client().delete('/questions/20000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):
        response = self.client().post('/questions', 
                                      json={'question':'Whose autobiography is entitled \'I Know Why the Caged Bird Sings\'?',
                                            'answer':'Tom Cruise',
                                            'category':'5',
                                            'difficulty':'4'})
        
        data = json.loads(response.data)
  
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['created'])

    def test_add_question_failure(self):
        response = self.client().post('/questions', 
                                      json={'question':None,
                                            'answer':None,
                                            'category':'5',
                                            'difficulty':'4'})
        
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable request')


    def test_search_question(self):
        response = self.client().post('/questions/search', json={'searchTerm':'Art'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertIsNotNone(data['total_questions'])
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])

    def test_search_question_failure(self):
        response = self.client().post('/questions/search', json={'searchTerm':None})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable request')

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_category_failure(self):
        response = self.client().get('/categories/20000/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        
    def test_post_quizzes(self):
        response = self.client().post('/quizzes', json={
            'previous_questions': [7],
            'quiz_category': {
                'type': 'Art',
                'id': '3'
            }
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 3)

    def test_post_quizzes_failure(self):
        response = self.client().post('/quizzes', json={
            'previous_questions': [7],
            'quiz_category': None
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()