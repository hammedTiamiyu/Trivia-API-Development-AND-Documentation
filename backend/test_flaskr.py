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
       
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres', 'codingly#22', 'localhost:5432', self.database_name) 
        setup_db(self.app, self.database_path)

        self.new_question =  {
                        "question": "Which year Nigeria gained their independence?",
                        "answer": "1960",
                        "difficulty": 2,
                        "category": "4"
                        }
        
        self.played_previous_questions_in_a_category = {
                            "previous_questions": [16, 17],
                            "quiz_category": {"id": 2, "type": "Art"}
                        }

        self.all_questions_in_a_category_played = {
                            "previous_questions": [16, 17, 18, 19],
                            "quiz_category": {"id": 2, "type": "Art"}
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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=505", json={"rating": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # def test_delete_question(self):
    #     res = self.client().delete('/questions/2')
    #     data = json.loads(res.data)

    #     book = Question.query.filter(Question.id == 2).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass

    # def test_422_if_question_creation_fails(self):
    #     res = self.client().post("/questions", json=self.new_question)
    #     data = json.loads(res.data)
    #     pass

    def test_get_questions_search_with_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "Organ"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_questions_search_without_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "teleport"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["currentCategory"],"Art")

    def test_404_sent_requesting_invalid_category(self):
        res = self.client().get("/categories/66/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quizzes_with_results(self):
        res = self.client().post("/quizzes", json= self.played_previous_questions_in_a_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_play_quizzes_with_all_questions_played(self):
        res = self.client().post("/quizzes", json= self.all_questions_in_a_category_played)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"], None)
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()