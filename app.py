import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr, constr, conlist, ValidationError
from typing import List, Optional
from enum import Enum
from config import MONGO_URI
import pytest

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
    email: EmailStr

# Endpoints for CVs
@app.route('/api/cvs/<email>', methods=['GET', 'DELETE'])
def get_cvs(email):
    if request.method == 'GET':
        cvs = list(cv_collection.find({'email': email}, {'_id': 0}))  # Exclude _id from results
        if len(cvs) == 0:
            return jsonify({'error': 'No CVs found'}), 404
        else:
            return jsonify({
                'status': 'success',
                'message': 'CVs retrieved successfully',
                'data': cvs
            })
    else:
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

# Endpoints for Events
@app.route('/api/events/<email>', methods=['GET', 'DELETE'])
def get_events(email):
    if request.method == 'GET':
        events = list(event_collection.find({'email': email}, {'_id': 0}))
        if len(events)>0:
            return jsonify({
                'status': 'success',
                'message': 'Events retrieved successfully',
                'data': events
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No events found for the given email'
            }), 404


    else:
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


@app.route('/api/add_event', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)

def test_valid_cv_model():
    valid_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "summary": "Experienced developer",
        "experience": "5 years",
        "education": "Bachelor's degree",
        "skills": "Python, Java"
    }
    cv = CV(**valid_data)
    assert cv.name == "John Doe"
    assert cv.email == "john@example.com"

def test_invalid_cv_model():
    invalid_data = {
        "name": "John Doe",
        "email": "invalid_email",
        "phone": "1234567890"
    }
    with pytest.raises(ValidationError):
        CV(**invalid_data)

def test_valid_event_model():
    valid_data = {
        "name": "Hackathon",
        "description": "A great event",
        "type": "hackathon",
        "direction": "backend",
        "skills": ["python", "java"],
        "experience_lvl": "junior",
        "email": "m@example.com",
    }
    event = Event(**valid_data)
    assert event.name == "Hackathon"

def test_invalid_event_model():
    invalid_data = {
        "name": "Hackathon",
        "description": "A great event",
        "type": "invalid_type",
        "direction": "backend",
        "skills": ["python", "java"],
        "experience_lvl": "junior"
    }
    with pytest.raises(ValidationError):
        Event(**invalid_data)

