from flask import Flask, Blueprint
from flask_cors import CORS
from models import db
from routes import api
from config import Config

app = Flask(__name__)
app.config.from_object(Config) 

CORS(app)

db.init_app(app)
app.register_blueprint(api)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)
