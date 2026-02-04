from db import get_db_connection, init_database

init_database()

conn = get_db_connection()
cur = conn.cursor()

# DEV ONLY: clear old data
cur.execute("DELETE FROM choices")
cur.execute("DELETE FROM pages")
cur.execute("DELETE FROM stories")
conn.commit()

# Insert story
cur.execute("""
    INSERT INTO stories (title, description, author_name)
    VALUES (%s, %s, %s)
    RETURNING id
""", (
    "Mohith Exam Day",
    "A chaotic trip from La Defense to EPITA for a Python exam.",
    "System"
))
story_id = cur.fetchone()["id"]

pages = {}

def add_page(key, content, is_start=False, is_ending=False):
    cur.execute("""
        INSERT INTO pages (story_id, page_key, content, is_start, is_ending)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (story_id, key, content, is_start, is_ending))
    pages[key] = cur.fetchone()["id"]

def add_choice(from_key, to_key, text, order, time_change=0):
    cur.execute("""
        INSERT INTO choices (from_page_id, to_page_id, choice_text, choice_order, time_change)
        VALUES (%s, %s, %s, %s, %s)
    """, (pages[from_key], pages[to_key], text, order, time_change))

# Pages

add_page("start", "Paris, La Defense. The night before his Python for Web exam. Mohith lies in bed with his phone. It is 23:47.", is_start=True)

add_page("sleep", "07:00. Mohith wakes up feeling okay. Today is the Python for Web exam at EPITA.")
add_page("overscroll", "Five minutes become forty. Mohith wakes up late and panics.")

add_page("check_bag", "Before leaving, Mohith thinks about his bag. Does he have his student card and calculator?")

add_page("leave_house", "Mohith rushes outside and heads to the metro at La Defense.")

add_page("metro_run", "The metro doors are closing.")
add_page("miss_train", "The metro leaves without him. He has to wait for the next one.")

add_page("in_metro", "Inside the metro. It is crowded and noisy.")

add_page("scroll_metro", "You start scrolling on your phone. One video becomes many.")

add_page("miss_station", "The doors close. That was your station. You missed it.")

add_page("backtrack", "You get off at the next stop and wait for the metro in the other direction.")

add_page("grandma", "A random grandma talks to you and asks if this metro goes to Chatelet.")

add_page("near_epita", "You get off near EPITA. The building is in sight.")

add_page("good_end", "You arrive on time and have everything. The exam begins. Good luck Mohith.", is_ending=True)
add_page("late_end", "You arrive too late. The doors are closed. Maybe scrolling was not worth it.", is_ending=True)

# Choices

add_choice("start", "sleep", "Go to sleep now", 1, 0)
add_choice("start", "overscroll", "Scroll five more minutes on Instagram", 2, 0)

add_choice("sleep", "check_bag", "Get up and get ready", 1, 0)
add_choice("overscroll", "check_bag", "Panic and get ready fast", 1, 10)

add_choice("check_bag", "leave_house", "Check bag quickly and leave", 1, 0)
add_choice("check_bag", "leave_house", "Do not check bag and leave", 2, 0)

add_choice("leave_house", "metro_run", "Run to catch the metro", 1, -5)
add_choice("leave_house", "miss_train", "Walk and check your phone", 2, 5)

add_choice("metro_run", "in_metro", "Jump inside at the last second", 1, -5)
add_choice("metro_run", "miss_train", "Miss the train", 2, 10)

add_choice("miss_train", "in_metro", "Wait for the next train", 1, 10)

add_choice("in_metro", "grandma", "Revise Python notes", 1, 0)
add_choice("in_metro", "scroll_metro", "Scroll social media", 2, 0)
add_choice("in_metro", "grandma", "Stare into space", 3, 5)

add_choice("scroll_metro", "miss_station", "Keep scrolling", 1, 10)
add_choice("scroll_metro", "grandma", "Stop and pay attention", 2, 0)

add_choice("miss_station", "backtrack", "Get off and go back", 1, 15)

add_choice("backtrack", "grandma", "Finally get back on track", 1, 0)

add_choice("grandma", "near_epita", "Help her and listen", 1, 5)
add_choice("grandma", "near_epita", "Give a quick answer and ignore", 2, 0)
add_choice("grandma", "near_epita", "Pretend you do not speak French", 3, 5)

add_choice("near_epita", "good_end", "Run to the building", 1, -5)
add_choice("near_epita", "late_end", "Walk and hope for the best", 2, 5)

conn.commit()
cur.close()
conn.close()

print("Story imported successfully!")
