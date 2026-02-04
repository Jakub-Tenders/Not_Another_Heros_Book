from db import get_db_connection


# -------- STORIES --------

def get_all_stories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stories ORDER BY created_at DESC")
    stories = cur.fetchall()
    cur.close()
    conn.close()
    return stories


def get_story_by_id(story_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stories WHERE id = %s", (story_id,))
    story = cur.fetchone()
    cur.close()
    conn.close()
    return story


# -------- PAGES --------

def get_start_page(story_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM pages
        WHERE story_id = %s AND is_start = TRUE
        LIMIT 1
    """, (story_id,))
    page = cur.fetchone()
    cur.close()
    conn.close()
    return page


def get_page_by_id(page_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pages WHERE id = %s", (page_id,))
    page = cur.fetchone()
    cur.close()
    conn.close()
    return page


# -------- CHOICES --------

def get_choices_for_page(page_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM choices
        WHERE from_page_id = %s
        ORDER BY choice_order ASC
    """, (page_id,))
    choices = cur.fetchall()
    cur.close()
    conn.close()
    return choices


def get_choice_by_id(choice_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM choices WHERE id = %s", (choice_id,))
    choice = cur.fetchone()
    cur.close()
    conn.close()
    return choice
