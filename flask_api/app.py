from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)

hostname = 'localhost'
database = 'storyline'
username = 'postgres'
pwd = '0000'
port_id = 5432

def get_db_connection():
    """Connect to PostgreSQL database"""
    conn = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id
    )
    return conn


@app.route('/api/health', methods=['GET'])
def health():
    """Test if API is working"""
    return jsonify({'status': 'healthy', 'message': 'Flask API is running'})


@app.route('/api/test-db', methods=['GET'])
def test_db():
    """Test database connection"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Database connected!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)