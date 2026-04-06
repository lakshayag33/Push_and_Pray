from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import date
from app.models import db, User, HealthLog, Suggestion
from app.services.score_engine import compute_score
from app.services.gemini_engine import analyze_quiz

mobile_api = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid token'}), 401
        token = auth_header.split(' ')[1]
        user = User.query.filter_by(api_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        return f(user, *args, **kwargs)
    return decorated

@mobile_api.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = user.api_token or user.generate_api_token()
        return jsonify({
            'success': True,
            'token': token,
            'user_id': user.id
        }), 200
    
    return jsonify({
        'success': False,
        'error': 'Invalid credentials'
    }), 401

@mobile_api.route('/submit_quiz', methods=['POST'])
@token_required
def submit_quiz(current_user):
    data = request.get_json() or {}
    
    # Check if already submitted today
    today = date.today()
    existing_log = HealthLog.query.filter_by(user_id=current_user.id, date=today).first()
    if existing_log:
        return jsonify({'error': 'Quiz already submitted today'}), 400
        
    try:
        log = HealthLog(
            user_id=current_user.id,
            date=today,
            sleep_hours=float(data.get('sleep_hours', 0)),
            sleep_time=data.get('sleep_time'),
            wake_time=data.get('wake_time'),
            screen_time_hours=float(data.get('screen_time_hours', 0)),
            steps=int(data.get('steps', 0)),
            calories=int(data.get('calories', 0)),
            water_ml=int(data.get('water_ml', 0)),
            stress_level=int(data.get('stress_level', 5)),
            mood=int(data.get('mood', 5)),
            sedentary_hours=float(data.get('sedentary_hours', 0)),
            outdoor_minutes=int(data.get('outdoor_minutes', 0)),
            exercise_minutes=int(data.get('exercise_minutes', 0)),
            breakfast_time=data.get('breakfast_time'),
            lunch_time=data.get('lunch_time'),
            dinner_time=data.get('dinner_time')
        )
        
        # Calculate score (needs an initialized log, even if not committed yet)
        score = compute_score(log)
        
        # We need recent history for gemini
        history = HealthLog.query.filter_by(user_id=current_user.id).order_by(HealthLog.date.desc()).limit(7).all()
        
        # Get AI suggestion
        ai_response = analyze_quiz(log, score, history)
        
        db.session.add(log)
        db.session.flush() # get log.id
        
        suggestion = Suggestion(
            user_id=current_user.id,
            log_id=log.id,
            score=score,
            suggestion_text=ai_response.get('suggestion', ''),
            status=ai_response.get('status', 'good'),
            urgent=ai_response.get('urgent', False)
        )
        
        db.session.add(suggestion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz saved successfully',
            'score': score
        }), 200
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mobile_api.route('/today_status', methods=['GET'])
@token_required
def today_status(current_user):
    today = date.today()
    existing_log = HealthLog.query.filter_by(user_id=current_user.id, date=today).first()
    return jsonify({
        'quiz_taken': existing_log is not None
    }), 200

@mobile_api.route('/recent_scores', methods=['GET'])
@token_required
def recent_scores(current_user):
    logs = HealthLog.query.filter_by(user_id=current_user.id).order_by(HealthLog.date.desc()).limit(3).all()
    results = []
    for log in logs:
        score = log.suggestion.score if log.suggestion else 0
        results.append({
            'date': log.date.isoformat(),
            'score': score
        })
    return jsonify(results), 200

@mobile_api.route('/validate', methods=['POST', 'GET'])
@token_required
def validate(current_user):
    return jsonify({
        'valid': True,
        'user_id': current_user.id
    }), 200
