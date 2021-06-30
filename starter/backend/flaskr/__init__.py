import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category
from sqlalchemy import func, and_

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  # CORS(app)

  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*": {"origins": "*"}})

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    if len(categories) == 0:
      abort(404)
    # formatted_json_categories=[category.format_2() for category in categories]
    categories_dict = {}
    for category in categories:
        categories_dict[category.id] = category.type

    return jsonify({
      'success': True,
      'categories': categories_dict # formatted_json_categories
    })


  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def questions_pagination(request, collection):
    page = request.args.get('page', 1, type=int)
    start_item = (page - 1) * QUESTIONS_PER_PAGE
    end_item = start_item + QUESTIONS_PER_PAGE
    questions = [question.format() for question in collection]
    current_questions = questions[start_item:end_item]
    return current_questions


  @app.route('/questions')
  @cross_origin()
  def get_all_questions():
    collection = Question.query.order_by(Question.category).all()
    current_questions = questions_pagination(request, collection)

    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.order_by(Category.id).all()
    categories_dict = {}
    for category in categories:
        categories_dict[category.id] = category.type
    # formatted_list_categories=[category.format() for category in categories]

    questions_count = len(Question.query.all())

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': questions_count,
      'categories': categories_dict,
      'current_category': categories_dict[1]
    })


  '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
      })
    except:
      abort(422)

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  

  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    json_body = request.get_json()
    question_input = json_body.get('question', None)
    answer_input = json_body.get('answer', None)
    category_input = json_body.get('category', None)
    difficulty_input = json_body.get('difficulty', None)
    search_input = json_body.get('searchTerm', None)

    try:
      if search_input:
        search_result = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_input)))
        current_questions = questions_pagination(request, search_result)
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(search_result.all()),
          'current_category': current_questions[0]['category']
        })
      else:
        question = Question(question=question_input, answer=answer_input, category=category_input, difficulty=difficulty_input)
        question.insert()
        return jsonify({
          'success': True
        })
    except:
      abort(422)


  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    collection = Question.query.filter(Question.category == category_id)
    current_questions = questions_pagination(request, collection)

    current_category = Category.query.filter(Category.id == category_id).one_or_none()
    current_category_dict = {category_id: current_category.type}

    questions_count = len(Question.query.all())

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': questions_count,
      'current_category': current_category_dict[category_id]
    })


  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quizzes():
    json_body = request.get_json()
    previous_question_ids = json_body.get('previous_questions')
    category_string = json_body.get('quiz_category')

    if previous_question_ids is None or category_string is None:
      abort(400)

    # category_id = Category.query.filter(Category.type == category_string['type']).one_or_none()

    if category_string['id'] == 0:  # if user select "ALL" questions in categories
      questions_query = Question.query.all()
    else:
      questions_query = Question.query.filter_by(category=category_string['id']).all()

    total_questions_count = len(questions_query)

    def generate_random_question():
      return questions_query[random.randrange(0, total_questions_count, 1)]

    def is_question_used(question):
      is_used = False
      for previous_question_id in previous_question_ids:
        if previous_question_id == question.id:
          is_used = True

      return is_used

    question = generate_random_question()

    while (is_question_used(question)):
      question = generate_random_question()
      if len(previous_question_ids) == total_questions_count:
        return jsonify({
          'success': True
        })

    return jsonify({
      'success': True,
      'question': question.format()
    })


  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400

  return app

    