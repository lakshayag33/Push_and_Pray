from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message


scheduler = BackgroundScheduler()


def init_scheduler(app, mail):
    """Initialize and start the APScheduler with two daily jobs."""

    def daily_reminder():
        """Job 1: Send reminder emails at 8:00 AM to users who haven't taken the quiz today."""
        with app.app_context():
            from app.models import db, User, HealthLog
            try:
                today = date.today()
                users = User.query.filter_by(role='user').all()
                for user in users:
                    has_log = HealthLog.query.filter_by(
                        user_id=user.id, date=today
                    ).first()
                    if not has_log and user.email:
                        try:
                            msg = Message(
                                subject="🌿 Daily Health Check Reminder",
                                recipients=[user.email],
                                body=(
                                    f"Hi {user.display_name},\n\n"
                                    "You haven't taken your daily health quiz yet. "
                                    "Take a few minutes to log your habits and get personalized suggestions!\n\n"
                                    "Stay healthy,\nYour Health Assistant"
                                )
                            )
                            mail.send(msg)
                        except Exception as e:
                            app.logger.error(f"Failed to send reminder to {user.email}: {e}")
            except Exception as e:
                app.logger.error(f"Daily reminder job error: {e}")

    def auto_analyze():
        """Job 2: Auto-analyze at 11:59 PM for users with quiz but no suggestion today."""
        with app.app_context():
            from app.models import db, HealthLog, Suggestion
            from app.services.score_engine import compute_score
            from app.services.gemini_engine import analyze_quiz
            try:
                today = date.today()
                logs = HealthLog.query.filter_by(date=today).all()
                for log in logs:
                    existing = Suggestion.query.filter_by(
                        user_id=log.user_id, log_id=log.id
                    ).first()
                    if not existing:
                        score = compute_score(log)
                        history = HealthLog.query.filter_by(
                            user_id=log.user_id
                        ).order_by(HealthLog.date.desc()).limit(7).all()
                        result = analyze_quiz(log, score, history)
                        suggestion = Suggestion(
                            user_id=log.user_id,
                            log_id=log.id,
                            score=score,
                            suggestion_text=result['suggestion'],
                            status=result['status'],
                            urgent=result['urgent']
                        )
                        db.session.add(suggestion)
                db.session.commit()
            except Exception as e:
                app.logger.error(f"Auto-analyze job error: {e}")

    scheduler.add_job(daily_reminder, 'cron', hour=8, minute=0, id='daily_reminder')
    scheduler.add_job(auto_analyze, 'cron', hour=23, minute=59, id='auto_analyze')

    if not scheduler.running:
        scheduler.start()
