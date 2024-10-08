import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


database_username = os.environ['DB_USER']
database_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
database_name = os.environ['DB_NAME']

database_path = 'postgresql://{}:{}@{}:{}/{}'.format(
    database_username,
    database_password,
    db_host,
    db_port,
    database_name
)

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_path = database_path
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["categories"]))

    def test_get_categories_failure(self):
        res = self.client().get("/categorie")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["messages"], "Page not found")

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["current_category"], '')
        self.assertTrue(data["categories"])

    def test_get_paginated_questions_by_page(self):
        res = self.client().get("/questions?page=100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["messages"], "Page not found")

    def test_delete_questions(self):
        # Create a new question or find an existing one
        question = Question(question="Sample Question", answer="Sample Answer", category="1", difficulty=1)
        db.session.add(question)
        db.session.commit()

        # Now attempt to delete the question
        res = self.client().delete(f"/questions/{question.id}")
        data = json.loads(res.data)

        # Check if the question was successfully deleted
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

        # Clean up by removing the question if it still exists
        question = Question.query.filter_by(id=question.id).first()
        if question:
            db.session.delete(question)
            db.session.commit()
    
    def test_delete_questions_not_found(self):
        res = self.client().delete("/questions/200")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["messages"], "Unprocessable entity")

    def test_create_new_question(self):
        res = self.client().post("/questions", json={
            "question": "New question",
            "answer": "New answer",
            "difficulty": 10,
            "category": 2
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])


    def test_create_new_question_failure(self):
        res = self.client().post("/questions", json={
            "question": "New question",
            "answer": "New answer",
            "difficulty": 10
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["messages"], "Unprocessable entity")

    def test_search_questions(self):
        res = self.client().post("/questions/search", json={
            "query": "question"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["current_category"], "")

    def test_search_questions_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["current_category"])

    def test_search_questions_by_category_failure(self):
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["messages"], "Unprocessable entity")

    def test_get_quiz_question(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": [],
            "category_id": 2
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], 2)

    def test_get_quiz_question_without_category(self):
        res = self.client().post("/quizzes", json={
            "previous_questions": []
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["messages"], "Unprocessable entity")

    def test_get_url_notfound(self):
        res = self.client().get("/test-url")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["messages"], "Page not found")
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()