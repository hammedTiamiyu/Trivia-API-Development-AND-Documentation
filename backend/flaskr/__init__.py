from ast import Num
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS



from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)    
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    selected_questions = questions[start:end]
    return selected_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
       
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
       
        return response
    
    @app.route('/categories', methods=['GET'])
    def hello():
        try:
            categories= {}
            queries = Category.query.all()
            for r in queries :
                categories[r.id]= r.type           
            return jsonify({
                "success": True,
                "categories" : categories
                })

        except: 
            abort(404)   
        
  
    @app.route('/questions', methods=["GET"])
    def get_paginated_questions():

        try:
            categories= {}
            queries = Category.query.all()
            for r in queries :
                categories[r.id]= r.type

            
            selection = Question.query.order_by(Question.id).all()           
            selected_questions = paginate_questions(request, selection)
            if len(selected_questions) == 0:
                abort(404)
            
            return jsonify(
                {
                    "questions" : selected_questions,
                    "total_questions": len(selection),
                    "categories" : categories,
                    "current_category": "History",
                    "success": True
                }
            )

        except: 
            abort(404)       
  
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
           
            queston = Question.query.filter(Question.id == question_id).one_or_none()
            if queston is None:
                abort(404)
            queston.delete()

            return jsonify({"success": True})
        except:
            abort(422)

    @app.route('/questions', methods=["POST"])
    def add_new_question():
        try:
            body= request.get_json()
            question = body.get("question", None)
            answer = body.get("answer", None)
            difficulty = body.get("difficulty", None)
            category = body.get("category", None)
            query = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            query.insert()
            return jsonify({"status": 200})
        except:
            abort(422)
   
    @app.route("/questions/search", methods=["POST"])
    def get_specific_question():
                        
        searchTerm= request.get_json().get("searchTerm", None)
             
        try:
            selection = Question.query.filter(
                func.lower(Question.question).ilike('%'+str(searchTerm).lower()+'%')).all()
            selected_questions = paginate_questions(request, selection)
                       
            return jsonify(
                {
                    "success": True,
                    "questions": selected_questions,
                    "total_questions": len(selected_questions),                    
                }
            )
        except:
            abort(422)

   
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            selection = Question.query.filter(Question.category == category_id).all()
            selected_questions = paginate_questions(request, selection)
            query = Category.query.get(category_id)
            current_category = query.type
            
            return jsonify (
                {
                    "success": True,
                    "questions": selected_questions,
                    "totalQuestions": len(selected_questions),
                    "currentCategory": current_category
                }
            )

        except:
            abort(404)
   
    @app.route('/quizzes', methods=["POST"])
    def play_question_per_quiz():
        try:
            body = request.get_json()
            previous_questions = body.get("previous_questions")           
            category = body.get("quiz_category")
            category_id = category['id']
            category_name = category['type']            
            # get question based on selected category
            if category_id==0:               
                selection = Question.query.order_by(func.random()).all()
                
            else:
              
                selection = Question.query.filter_by(category = category_id).order_by(func.random()).all()

            if len(previous_questions) == len(selection):
                return jsonify({
                    "success": True,
                    "question": None
                })
           
            for row in selection:
                if row.id not in previous_questions:
                    return jsonify(
                        {
                            "success": True,
                            "question": {
                                "id": row.id,
                                "question": row.question,
                                "answer": row.answer,
                                "difficulty": row.difficulty,
                                "category": category_id
                            }
                        }
                    )                 
            
        except:
            abort(404)

    
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return(
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )
    
    @app.errorhandler(400)
    def bad_request(error):
        return(
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(500)
    def bad_request(error):
        return(
            jsonify({"success": False, "error": 500, "message": "internal server error"}),
            500,
        )

    return app


   
