import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import cast, Integer
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
      return response

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def categories():
        categories = db.session.query(Category).all()
        categories_json = {category.id: category.type for category in categories}
        return jsonify({
            'success': True,
            'categories': categories_json
        })
    
    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10  ).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def questions():
        page = request.args.get('page', 1, type=int)
        questions = Question.query.order_by(Question.id).paginate(page,QUESTIONS_PER_PAGE,error_out=False).items
        questions_json = [question.format() for question in questions]
        categories = db.session.query(Category).all()
        categories_json = {category.id: category.type for category in categories}

        if len(questions_json) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions_json,
            'total_questions': len(questions),
            'categories': categories_json,
            'current_category': ''
        })
    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def del_questions(question_id):
        question = db.session.query(Question).get(question_id)
        
        if question is None:
            abort(422)
        question.delete()

        return jsonify({
            'success': True,
            "messages": "Question successfully deleted",
            "question_id": question_id
        })
    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_questions():
        data = request.get_json()

        if (
            "question" not in data
            or "answer" not in data
            or "difficulty" not in data
            or "category" not in data
        ):
            abort(422)
        
        Question(
            question=data["question"],
            answer=data["answer"],
            difficulty=data["difficulty"],
            category=data["category"],
        ).insert()
        return jsonify({
            'success': True
        })
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=["POST"])
    def search_questions():
        data = request.get_json()
        query = data["query"]
        questions = db.session.query(Question).filter(Question.question.ilike(f'%{query}%')).all()
        questions_json = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': questions_json,
            'total_questions': len(questions_json),
            'current_category': ''
        })
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def search_questions_by_category(category_id):
        questions = db.session.query(Question).filter(Question.category == category_id).all()
        questions_json = [question.format() for question in questions]
        category = db.session.query(Category).get(category_id)
        if category is None:
            abort(422)
        return jsonify({
            'success': True,
            'questions': questions_json,
            'total_questions': len(questions_json),
            'current_category': category.type
        })
    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=["POST"])
    def quizzes():
        data = request.get_json()
        # Validate request data
        if "category_id" not in data or "previous_questions" not in data:
            abort(422)
        
        previous_questions = data["previous_questions"]
        category_id = data["category_id"]
        
        # Query database for questions
        if category_id == 0:  # If "All" categories selected
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:  # If a specific category is selected
            questions = Question.query.filter(Question.category == category_id, Question.id.notin_(previous_questions)).all()
        
        # Select a random question
        result = {"success": True}
        if questions:
            question = random.choice(questions)
            result["question"] = question.format()  # Assuming Question model has a format method for serialization
        
        return jsonify(result)
    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'messages': 'Bad request',
            "error": 400,
        }), 400
    
    @app.errorhandler(422)
    def unprocessable_request(error):
        return jsonify({
            "success": False,
            'messages': "Unprocessable entity",
            "error": 422,
        }), 422
    
    @app.errorhandler(404)
    def not_found_request(error):
        return jsonify({
            "success": False,
            "messages": "Page not found",
            "error": 404,
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'messages': "Internal server error",
            "error": 500,
        }), 500
    return app

