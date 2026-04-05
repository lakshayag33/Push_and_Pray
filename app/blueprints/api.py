from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import HealthLog
from app.services.gemini_engine import chat_response

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/charts/<metric>')
@login_required
def charts(metric):
    """Return JSON chart data for the given metric. Supports user_id param for reviewers."""
    user_id = request.args.get('user_id', current_user.id, type=int)

    # Security: only allow viewing own data or reviewed user's data
    if user_id != current_user.id:
        if current_user.role != 'reviewer':
            return jsonify({'error': 'Forbidden'}), 403
        from app.models import ReviewerInvite
        invite = ReviewerInvite.query.filter_by(
            user_id=user_id,
            reviewer_id=current_user.id,
            status='accepted'
        ).first()
        if not invite:
            return jsonify({'error': 'Forbidden'}), 403

    today = date.today()
    week_ago = today - timedelta(days=6)

    logs = HealthLog.query.filter(
        HealthLog.user_id == user_id,
        HealthLog.date >= week_ago,
        HealthLog.date <= today
    ).order_by(HealthLog.date.asc()).all()

    valid_metrics = {
        'sleep': 'sleep_hours',
        'steps': 'steps',
        'mood': 'mood',
        'stress': 'stress_level',
        'water': 'water_ml',
        'calories': 'calories',
        'screen': 'screen_time_hours',
        'exercise': 'exercise_minutes',
        'outdoor': 'outdoor_minutes',
    }

    if metric not in valid_metrics:
        return jsonify({'error': 'Invalid metric'}), 400

    field = valid_metrics[metric]
    labels = []
    data = []

    for log in logs:
        labels.append(log.date.strftime('%b %d'))
        data.append(getattr(log, field, 0))

    return jsonify({
        'labels': labels,
        'data': data,
        'metric': metric
    })


@api_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Chatbot endpoint. Receives message and conversation, returns AI reply."""
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'Invalid request'}), 400

    message = payload.get('message', '').strip()
    conversation = payload.get('conversation', [])

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    today = date.today()
    week_ago = today - timedelta(days=7)

    today_log = HealthLog.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    history = HealthLog.query.filter(
        HealthLog.user_id == current_user.id,
        HealthLog.date >= week_ago,
        HealthLog.date <= today
    ).order_by(HealthLog.date.desc()).all()

    result = chat_response(message, conversation, today_log, history)

    return jsonify({
        'reply': result['reply'],
        'urgent': result['urgent']
    })
