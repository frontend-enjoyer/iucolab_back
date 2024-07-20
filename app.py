import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr, constr, conlist
from typing import List, Optional
from enum import Enum
from config import MONGO_URI

app = Flask(__name__)
client = MongoClient(MONGO_URI)
db = client["iuCollab"]

cv_collection = db['cvs']
event_collection = db['events']


# Enum definitions for validation
class EventType(str, Enum):
    hackathon = "hackathon"
    vacancy = "vacancy"


class Direction(str, Enum):
    backend = "backend"
    frontend = "frontend"
    ml = "ml"
    ux_ui = "ux/ui"
    business_analytics = "business analytics"
    gamedev = "gamedev"


class Skill(str, Enum):
    python = "python"
    java = "java"
    c_plus_plus = "c++"
    c = "c"
    c_sharp = "c#"
    go = "go"
    html_css = "html/css"
    flutter = "flutter"
    swift = "swift"
    kotlin = "kotlin"


class ExperienceLevel(str, Enum):
    junior = "junior"
    middle = "middle"
    senior = "senior"


# Define Pydantic models for validation
class CV(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr  # Validate email format
    phone: constr(min_length=1)  # Ensure phone is not empty, adjust as needed
    summary: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None


class Event(BaseModel):
    name: str
    description: str
    type: EventType
    direction: Direction
    skills: List[Skill]
    experience_lvl: ExperienceLevel


# Endpoints for CVs
@app.route('/api/cvs/<email>', methods=['GET'])
def get_cvs(email):
    cvs = list(cv_collection.find({'email': email}, {'_id': 0}))  # Exclude _id from results
    if len(cvs) == 0:
        return jsonify({'error': 'No CVs found'}), 404
    else:
        return jsonify({
            'status': 'success',
            'message': 'CVs retrieved successfully',
            'data': cvs
        })


@app.route('/api/cvs', methods=['POST'])
def add_cv():
    try:
        data = CV(**request.json)
        cv_collection.insert_one(data.dict())
        return jsonify({
            'status': 'success',
            'message': 'CV added successfully',
            'data': data.dict()
        }), 201
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': str(e)
        }), 400


@app.route('/api/cvs/<email>', methods=['DELETE'])
def delete_cvs(email):
    result = cv_collection.delete_many({'email': email})
    if result.deleted_count > 0:
        return jsonify({
            'status': 'success',
            'message': f'{result.deleted_count} CV(s) deleted successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'No CVs found for the given email'
        }), 404


# Endpoints for Events
@app.route('/api/events/<email>', methods=['GET'])
def get_events(email):
    events = list(event_collection.find({'email': email}, {'_id': 0}))  # Exclude _id from results
    return jsonify({
        'status': 'success',
        'message': 'Events retrieved successfully',
        'data': events
    })


@app.route('/api/events', methods=['POST'])
def add_event():
    try:
        data = Event(**request.json)
        event_collection.insert_one(data.dict())
        return jsonify({
            'status': 'success',
            'message': 'Event added successfully',
            'data': data.dict()
        }), 201
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': str(e)
        }), 400


@app.route('/api/events/<email>', methods=['DELETE'])
def delete_events(email):
    result = event_collection.delete_many({'email': email})
    if result.deleted_count > 0:
        return jsonify({
            'status': 'success',
            'message': f'{result.deleted_count} event(s) deleted successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'No events found for the given email'
        }), 404


if __name__ == '__main__':
    app.run(debug=True)
