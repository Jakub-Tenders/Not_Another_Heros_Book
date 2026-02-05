from flask import Flask, Blueprint
from models import db
from routes import api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql://postgres:0000@localhost:5432/storyline"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(api)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
