from flask import Flask
from backend.models import db
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = None


def setup_app():
    app  = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///Jobfinder.sqlite3" #Having db file
    db.init_app(app) #Flask app connected to db(SQL alchemy)
    app.app_context().push() #Direct access to other modules
    app.debug=True
    print("Jobfinder app is started...")
    return app


#Call the setup
app = setup_app()

from backend.controllers import * 

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(role = "admin").first()
        # Admin created only once
        if user is None:
            user = User(email = os.getenv("ADMIN_EMAIL"), password = generate_password_hash(os.getenv("ADMIN_PASSWORD")), role = os.getenv("ROLE"))
            db.session.add(user)
            db.session.commit()
    app.run()