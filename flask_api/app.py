from flask import Flask
from routes import api
from db import init_database

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)

    
    init_database()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
