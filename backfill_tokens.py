from app import create_app
from app.models import db, User

app = create_app()
with app.app_context():
    count = 0
    for user in User.query.all():
        if not user.api_token:
            user.generate_api_token()
            count += 1
    print(f"Tokens generated for {count} existing users.")
