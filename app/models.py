from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user | reviewer | admin
    reviewer_status = db.Column(db.String(20), nullable=True)  # pending | active | rejected | null
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    api_token = db.Column(db.String(64), unique=True, nullable=True)

    health_logs = db.relationship('HealthLog', backref='user', lazy='dynamic')
    suggestions = db.relationship('Suggestion', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def generate_api_token(self):
        import secrets
        self.api_token = secrets.token_urlsafe(32)
        db.session.commit()
        return self.api_token

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        return self.email.split('@')[0]


class HealthLog(db.Model):
    __tablename__ = 'health_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    sleep_hours = db.Column(db.Float, nullable=False, default=0)
    sleep_time = db.Column(db.String(5), nullable=True)   # HH:MM
    wake_time = db.Column(db.String(5), nullable=True)     # HH:MM
    screen_time_hours = db.Column(db.Float, nullable=False, default=0)
    steps = db.Column(db.Integer, nullable=False, default=0)
    calories = db.Column(db.Integer, nullable=False, default=0)
    water_ml = db.Column(db.Integer, nullable=False, default=0)
    stress_level = db.Column(db.Integer, nullable=False, default=5)   # 1-10
    mood = db.Column(db.Integer, nullable=False, default=5)           # 1-10
    sedentary_hours = db.Column(db.Float, nullable=False, default=0)
    outdoor_minutes = db.Column(db.Integer, nullable=False, default=0)
    exercise_minutes = db.Column(db.Integer, nullable=False, default=0)
    breakfast_time = db.Column(db.String(5), nullable=True)  # HH:MM
    lunch_time = db.Column(db.String(5), nullable=True)      # HH:MM
    dinner_time = db.Column(db.String(5), nullable=True)     # HH:MM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    suggestion = db.relationship('Suggestion', backref='health_log', uselist=False)

    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'sleep_hours': self.sleep_hours,
            'sleep_time': self.sleep_time,
            'wake_time': self.wake_time,
            'screen_time_hours': self.screen_time_hours,
            'steps': self.steps,
            'calories': self.calories,
            'water_ml': self.water_ml,
            'stress_level': self.stress_level,
            'mood': self.mood,
            'sedentary_hours': self.sedentary_hours,
            'outdoor_minutes': self.outdoor_minutes,
            'exercise_minutes': self.exercise_minutes,
            'breakfast_time': self.breakfast_time,
            'lunch_time': self.lunch_time,
            'dinner_time': self.dinner_time,
        }


class Suggestion(db.Model):
    __tablename__ = 'suggestions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    log_id = db.Column(db.Integer, db.ForeignKey('health_logs.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)  # 0-100
    suggestion_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='good')  # excellent | good | needs_improvement
    urgent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ReviewerInvite(db.Model):
    __tablename__ = 'reviewer_invites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)      # user sending invite
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # reviewer receiving it
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending | accepted | revoked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='sent_invites')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='received_invites')
