import os
from flask import Flask, request, abort, jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# method for paginating questions
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    if test_config:
        app.config.from_mapping(test_config)
    else:
        setup_db(app)

    # set up CORS, allowing all origins
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, DELETE, PATCH, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type,true')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    #fetches a dictionary of categories
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            #get all categories
            categories = Category.query.all()
            # abort 404 if no categories found
            if len(categories) == 0:
                abort(404)
            #return data to view
            return jsonify({
                'categories': {category.id: category.type for category in categories}
            })
        except Exception as e:
            print(e)
            abort(500)

    #fetches a paginated set of questions, a total number of questions, all categories and current category string
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            request.args.get('page', 1, type=int)
            questions = Question.query.all()
            totalQuestions = len(questions)
            # abort 404 if total questions are not greater than 0
            if(totalQuestions == 0):
                abort(404)
            categories = Category.query.all()
            #return data to view
            return jsonify({
                'total_questions': totalQuestions,
                'current_category': None,
                'questions': paginate_questions(request, questions),
                'categories': {category.id: category.type for category in categories}
            })

        except Exception as e:
            print(e)
            abort(500)


    #delete question based on id
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        #fetches question from DB based on id
        question = Question.query.filter_by(id=question_id).one_or_none()
        # abort 404 if no question found
        if question is None:
            abort(404)
        try:
            question.delete()
            #return data to view
            return jsonify({
                'success': True,
            })

        except Exception as e:
            print(e)
            abort(500)

    #add question 
    @app.route('/questions', methods=['POST'])
    def add_question():
        data = request.get_json()

        #abort 422 if no data found
        if(data == None):
            abort(422)

        question = data.get('question')
        answer = data.get('answer')
        category = data.get('category')
        difficulty = data.get('difficulty')

        #abort 422 if any field not found
        if any(field is None for field in [question, answer, category, difficulty]):
            abort(422)

        try:
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            question.insert()
            #return data to view
            return jsonify({
                'success': True,
                'total_questions': Question.query.count(),
                'created': question.id,
                'questions': paginate_questions(request, Question.query.all())
            })

        except Exception as e:
            print(e)
            abort(422)

    #search questions based on search term
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')
        #abort 422 if no serch_term found
        if search_term == None:
            abort(422)

        try:
            #fetches questions based on search term
            matching_questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')
            ).all()
            #return data to view
            return jsonify({
                'success': True,
                'questions': paginate_questions(request, matching_questions),
                'total_questions': len(matching_questions)
            })

        except Exception as e:
            print(e)
            abort(500)

    #Fetches questions based on category id
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        #fetched category based on id
        category = Category.query.filter_by(id=category_id).one_or_none()

        #abort 404 if no category found
        if category == None:
            abort(404)
        try:
            #fetches questions based on category id
            category_questions = Question.query.filter_by(category=category_id).all()
            #return data to view
            return jsonify({
                'success': True,
                'total_questions': len(category_questions),
                'questions': paginate_questions(request, category_questions),
                'current_category': category.format()
            })

        except Exception as e:
            print(e)
            abort(500)

    #fetches quiz questions
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz = data.get('quiz_category')
        #abort 400 if no quiz found
        if quiz == None:
            abort(400)

        category_id = int(quiz['id'])
        #fetches category based on id
        category = Category.query.filter_by(id=category_id).one_or_none()

        #abort 404 if no category found
        if category == None:
            abort(404)
        try:
            questions = Question.query.filter(
                Question.category == category_id,
                ~Question.id.in_(previous_questions)
            ).all()
            #return data to view
            return jsonify({
                'success': True,
                'question': random.choice(questions).format() if questions else None
            })

        except Exception as e:
            print(e)
            abort(500)
    
    @app.errorhandler(422)
    def unprocessed(error):
        return(
            jsonify({'success': False, 'error': 422,'message': 'Unprocessable request'}),
            422
        )
    
    @app.errorhandler(404)
    def not_found(error):
        return( 
            jsonify({'success': False, 'error': 404,'message': 'resource not found'}),
            404
        )

    @app.errorhandler(500)
    def server_error(error):
        return(
            jsonify({'success': False, 'error': 500,'message': 'internal server error'}),
            500
        )
    
    @app.errorhandler(400)
    def bad_request(error):
        return(
            jsonify({'success': False, 'error': 400,'message': 'bad request'}),
            400
        )
    
    @app.errorhandler(405)
    def bad_request(error):
        return(
            jsonify({'success': False, 'error': 405,'message': 'method not allowed'}),
            405
        )

    return app

