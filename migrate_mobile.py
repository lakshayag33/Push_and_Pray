from app import create_app
from app.models import db, User
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 1. SQL Migration
    try:
        db.session.execute(text("ALTER TABLE users ADD COLUMN api_token VARCHAR(64) UNIQUE;"))
        db.session.commit()
        print("Successfully added api_token column to users table.")
    except Exception as e:
        print("Notice on column addition (may already exist):", e)
    
    # 2. Token generation
    count = 0
    for user in User.query.all():
        if not user.api_token:
            user.generate_api_token()
            count += 1
    print(f"Tokens generated for {count} existing users.")
