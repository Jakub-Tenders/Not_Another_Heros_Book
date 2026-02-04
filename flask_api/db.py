import psycopg2
from psycopg2.extras import RealDictCursor
from conn import DB_CONN


def get_db_connection():
    """Get PostgreSQL database connection"""
    conn = psycopg2.connect(
        host=DB_CONN['host'],
        dbname=DB_CONN['database'],
        user=DB_CONN['user'],
        password=DB_CONN['password'],
        port=DB_CONN['port'],
        cursor_factory=RealDictCursor
    )
    return conn


def init_database():
    """Create database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            author_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id SERIAL PRIMARY KEY,
            story_id INTEGER REFERENCES stories(id) ON DELETE CASCADE,
            page_key VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            is_start BOOLEAN DEFAULT FALSE,
            is_ending BOOLEAN DEFAULT FALSE,
            page_number INTEGER,
            metadata JSONB
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS choices (
            id SERIAL PRIMARY KEY,
            from_page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
            to_page_id INTEGER REFERENCES pages(id) ON DELETE CASCADE,
            choice_text VARCHAR(500) NOT NULL,
            choice_order INTEGER DEFAULT 0,
            time_change INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Database tables initialized!")