from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, HealthLog, Suggestion, User, ReviewerInvite
from app.services.score_engine import compute_score
from app.services.gemini_engine import analyze_quiz

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.panel'))
        elif current_user.role == 'reviewer':
            return redirect(url_for('reviewer.dashboard'))
        return redirect(url_for('user.dashboard'))
    return render_template('main/index.html')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'user':
        if current_user.role == 'admin':
            return redirect(url_for('admin.panel'))
        return redirect(url_for('reviewer.dashboard'))

    today = date.today()
    today_log = HealthLog.query.filter_by(user_id=current_user.id, date=today).first()
    today_suggestion = None
    if today_log:
        today_suggestion = Suggestion.query.filter_by(
            user_id=current_user.id, log_id=today_log.id
        ).first()

    # Check if user has any data at all
    total_logs = HealthLog.query.filter_by(user_id=current_user.id).count()
    has_data = total_logs > 0
    quiz_taken_today = today_log is not None

    # Prepare template data
    score = today_suggestion.score if today_suggestion else None
    suggestion_text = today_suggestion.suggestion_text if today_suggestion else None
    suggestion_status = today_suggestion.status if today_suggestion else None
    suggestion_urgent = today_suggestion.urgent if today_suggestion else False

    # Reviewer invitations
    sent_invites = ReviewerInvite.query.filter_by(user_id=current_user.id).all()
    invite_data = []
    for inv in sent_invites:
        reviewer = User.query.get(inv.reviewer_id)
        if reviewer:
            invite_data.append({
                'id': inv.id,
                'reviewer_email': reviewer.email,
                'reviewer_name': reviewer.display_name,
                'status': inv.status,
                'created_at': inv.created_at
            })

    return render_template('user/dashboard.html',
                           score=score,
                           suggestion_text=suggestion_text,
                           suggestion_status=suggestion_status,
                           suggestion_urgent=suggestion_urgent,
                           has_data=has_data,
                           quiz_taken_today=quiz_taken_today,
                           invites=invite_data)


@user_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if current_user.role != 'user':
        return redirect(url_for('user.dashboard'))

    today = date.today()
    existing_log = HealthLog.query.filter_by(user_id=current_user.id, date=today).first()
    if existing_log:
        flash('You have already submitted the quiz today. Come back tomorrow!', 'info')
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        try:
            log = HealthLog(
                user_id=current_user.id,
                date=today,
                sleep_hours=float(request.form.get('sleep_hours', 0)),
                sleep_time=request.form.get('sleep_time', '') or None,
                wake_time=request.form.get('wake_time', '') or None,
                screen_time_hours=float(request.form.get('screen_time_hours', 0)),
                steps=int(request.form.get('steps', 0)),
                calories=int(request.form.get('calories', 0)),
                water_ml=int(request.form.get('water_ml', 0)),
                stress_level=int(request.form.get('stress_level', 5)),
                mood=int(request.form.get('mood', 5)),
                sedentary_hours=float(request.form.get('sedentary_hours', 0)),
                outdoor_minutes=int(request.form.get('outdoor_minutes', 0)),
                exercise_minutes=int(request.form.get('exercise_minutes', 0)),
                breakfast_time=request.form.get('breakfast_time', '') or None,
                lunch_time=request.form.get('lunch_time', '') or None,
                dinner_time=request.form.get('dinner_time', '') or None,
            )
            db.session.add(log)
            db.session.commit()

            # Compute score
            score = compute_score(log)

            # Get 7-day history
            week_ago = today - timedelta(days=7)
            history = HealthLog.query.filter(
                HealthLog.user_id == current_user.id,
                HealthLog.date >= week_ago,
                HealthLog.date <= today
            ).order_by(HealthLog.date.desc()).all()

            # Call Gemini
            result = analyze_quiz(log, score, history)

            # Save suggestion
            suggestion = Suggestion(
                user_id=current_user.id,
                log_id=log.id,
                score=score,
                suggestion_text=result['suggestion'],
                status=result['status'],
                urgent=result['urgent']
            )
            db.session.add(suggestion)
            db.session.commit()

            flash('Quiz submitted successfully!', 'success')
            return redirect(url_for('user.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting quiz. Please try again.', 'danger')
            return render_template('user/quiz.html')

    return render_template('user/quiz.html')


@user_bp.route('/history')
@login_required
def history():
    if current_user.role != 'user':
        return redirect(url_for('user.dashboard'))

    page = request.args.get('page', 1, type=int)
    logs = HealthLog.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthLog.date.desc()).paginate(page=page, per_page=10, error_out=False)

    log_data = []
    for log in logs.items:
        suggestion = Suggestion.query.filter_by(log_id=log.id).first()
        log_data.append({
            'date': log.date.strftime('%B %d, %Y'),
            'sleep_hours': log.sleep_hours,
            'steps': log.steps,
            'calories': log.calories,
            'water_ml': log.water_ml,
            'stress_level': log.stress_level,
            'mood': log.mood,
            'score': suggestion.score if suggestion else None,
            'status': suggestion.status if suggestion else None,
            'suggestion': suggestion.suggestion_text if suggestion else None,
            'urgent': suggestion.urgent if suggestion else False,
        })

    return render_template('user/history.html',
                           logs=log_data,
                           pagination=logs)


@user_bp.route('/chatbot')
@login_required
def chatbot():
    if current_user.role != 'user':
        return redirect(url_for('user.dashboard'))
    return render_template('user/chatbot.html')


@user_bp.route('/invite_reviewer', methods=['POST'])
@login_required
def invite_reviewer():
    if current_user.role != 'user':
        return redirect(url_for('user.dashboard'))

    reviewer_email = request.form.get('reviewer_email', '').strip().lower()
    reviewer = User.query.filter_by(email=reviewer_email, role='reviewer', reviewer_status='active').first()

    if not reviewer:
        flash('No active reviewer found with that email.', 'danger')
        return redirect(url_for('user.dashboard'))

    existing = ReviewerInvite.query.filter_by(
        user_id=current_user.id, reviewer_id=reviewer.id
    ).filter(ReviewerInvite.status != 'revoked').first()

    if existing:
        flash('You already have an active invitation with this reviewer.', 'warning')
        return redirect(url_for('user.dashboard'))

    invite = ReviewerInvite(
        user_id=current_user.id,
        reviewer_id=reviewer.id,
        status='pending'
    )
    db.session.add(invite)
    db.session.commit()
    flash('Invitation sent to reviewer!', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/revoke_invite/<int:invite_id>', methods=['POST'])
@login_required
def revoke_invite(invite_id):
    invite = ReviewerInvite.query.get_or_404(invite_id)
    if invite.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('user.dashboard'))

    invite.status = 'revoked'
    db.session.commit()
    flash('Invitation revoked.', 'info')
    return redirect(url_for('user.dashboard'))
