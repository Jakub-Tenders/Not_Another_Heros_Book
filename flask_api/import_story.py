from flask import Flask
from models import db, Story, Page, Choice
from config import Config

'''
     STORY FILE MADE BY AI (IDEA BY JAKUB AND TRISTAN)
'''

# --- Flask app setup ---
app = Flask(__name__)
app.config.from_object(Config)  # USE CONFIG INSTEAD OF HARDCODED
db.init_app(app)

# --- The story content ---
MOHITH_STORY = {
    "title": "Mohith's Python Exam Adventure",
    "description": "Mohith navigates Paris and crazy obstacles on his way to EPITA for his Python for Web exam.",
    "author_name": "Jakub",
    "pages": [
        {
            "page_key": "night_before_exam",
            "content": "It's the night before Mohith's Python for Web exam. Do you go to sleep or scroll 5 more minutes on Instagram?",
            "is_start": True,
            "choices": [
                {"choice_text": "Go to sleep", "next_page_key": "wake_up_early"},
                {"choice_text": "Scroll 5 more minutes", "next_page_key": "wake_up_late"}
            ]
        },
        {
            "page_key": "wake_up_early",
            "content": "Mohith wakes up early and prepares calmly. He grabs his student card and calculator. You hear your dad in the shower.",
            "choices": [
                {"choice_text": "Check the shower quickly", "next_page_key": "hot_water_off"},
                {"choice_text": "Ignore and leave for metro", "next_page_key": "metro_good"}
            ]
        },
        {
            "page_key": "wake_up_late",
            "content": "Mohith overslept and is late. He forgot his calculator.",
            "choices": [
                {"choice_text": "Rush to EPITA anyway", "next_page_key": "metro_bad"},
                {"choice_text": "Call a friend for notes", "next_page_key": "friend_help"}
            ]
        },
        {
            "page_key": "hot_water_off",
            "content": "Your dad turned off the hot water just as Mohith gets in. You freeze but manage to get ready faster.",
            "choices": [
                {"choice_text": "Rush to metro", "next_page_key": "metro_good"},
                {"choice_text": "Skip breakfast to save time", "next_page_key": "metro_good"}
            ]
        },
        {
            "page_key": "metro_good",
            "content": "The metro ride is smooth. You arrive early at EPITA. Nothing seems wrong, yet...",
            "choices": [
                {"choice_text": "Check your calculator just in case", "next_page_key": "exam_ready"},
                {"choice_text": "Relax and wait in the hall", "next_page_key": "exam_ready"},
                {"choice_text": "Help an old lady with her bag on the metro", "next_page_key": "extra_metro_event"}
            ]
        },
        {
            "page_key": "extra_metro_event",
            "content": "While helping the old lady, the metro slows down because a street performer is playing too loudly. Mohith arrives slightly late but still manages to enter the exam hall.",
            "choices": [
                {"choice_text": "Rush to your seat", "next_page_key": "pigeon_attack"},
                {"choice_text": "Take a deep breath and relax", "next_page_key": "pigeon_attack"}
            ]
        },
        {
            "page_key": "pigeon_attack",
            "content": "On the way from the metro to EPITA, a flock of pigeons suddenly swoops down! Mohith ducks, spins, and barely avoids disaster. Your backpack gets a little messy.",
            "choices": [
                {"choice_text": "Run to the exam hall", "next_page_key": "exam_ready"},
                {"choice_text": "Take a moment to clean yourself up", "next_page_key": "exam_ready"}
            ]
        },
        {
            "page_key": "metro_bad",
            "content": "On the metro, Mohith scrolls Instagram and misses his station. A friendly grandma points him in the right direction, but time is running out.",
            "choices": [
                {"choice_text": "Run to EPITA quickly", "next_page_key": "exam_late_no_entry"},
                {"choice_text": "Try to take another metro line", "next_page_key": "metro_extra_delay"},
                {"choice_text": "Stop and thank grandma for advice", "next_page_key": "metro_extra_delay"}
            ]
        },
        {
            "page_key": "friend_help",
            "content": "Your friend sends you the notes and a quick summary. You feel more confident, but time is short.",
            "choices": [
                {"choice_text": "Take metro quickly", "next_page_key": "metro_good"},
                {"choice_text": "Review notes on metro", "next_page_key": "metro_bad"}
            ]
        },
        {
            "page_key": "metro_extra_delay",
            "content": "The alternative metro line is delayed due to construction. Mohith runs as fast as he can, but the clock is ticking.",
            "choices": [
                {"choice_text": "Keep running", "next_page_key": "exam_late_no_entry"},
                {"choice_text": "Call a taxi", "next_page_key": "taxi_rush"}
            ]
        },
        {
            "page_key": "taxi_rush",
            "content": "You take a taxi, but traffic slows you down. Mohith barely reaches the EPITA gate.",
            "choices": [
                {"choice_text": "Run to the exam hall", "next_page_key": "exam_late_no_entry"},
                {"choice_text": "Give up and wait for next exam", "next_page_key": "exam_missed"}
            ]
        },
        {
            "page_key": "exam_ready",
            "content": "Mohith sits in the exam hall prepared. Everything is ready, and you feel confident. Good luck!",
            "is_ending": True
        },
        {
            "page_key": "exam_late_no_entry",
            "content": "Mohith arrives too late. The exam hall door is closed. Entry is forbidden. He misses the exam!",
            "is_ending": True
        },
        {
            "page_key": "exam_missed",
            "content": "Mohith missed the exam entirely. Time to reschedule and prepare for next attempt.",
            "is_ending": True
        }
    ]
}


# --- Helper function to get page by key ---
def get_page_by_key(pages, key):
    for p in pages:
        if p.page_key == key:
            return p
    return None

# --- Import function ---
def import_mohith_story():
    with app.app_context():
        db.create_all()
        print("✓ Tables created")
        
        # 1. Create story
        story = Story(
            title=MOHITH_STORY["title"],
            description=MOHITH_STORY["description"],
            author_name=MOHITH_STORY["author_name"]
        )
        db.session.add(story)
        db.session.commit()

        pages = []

        # 2. Create pages
        for p_data in MOHITH_STORY["pages"]:
            page = Page(
                story_id=story.id,
                page_key=p_data["page_key"],
                content=p_data["content"],
                is_start=p_data.get("is_start", False),
                is_ending=p_data.get("is_ending", False)
            )
            db.session.add(page)
            pages.append(page)

        db.session.commit()  # commit to get page IDs

        # 3. Set start_page_id
        start_page = next((p for p in pages if p.is_start), None)
        if start_page:
            story.start_page_id = start_page.id
            db.session.commit()

        # 4. Create choices
        for p_data in MOHITH_STORY["pages"]:
            from_page = get_page_by_key(pages, p_data["page_key"])
            for c_data in p_data.get("choices", []):
                to_page = get_page_by_key(pages, c_data["next_page_key"])
                if to_page:
                    choice = Choice(
                        from_page_id=from_page.id,
                        to_page_id=to_page.id,
                        choice_text=c_data["choice_text"]
                    )
                    db.session.add(choice)

        db.session.commit()
        print("✓ Mohith story imported successfully!")

# --- Run import ---
if __name__ == "__main__":
    import_mohith_story()