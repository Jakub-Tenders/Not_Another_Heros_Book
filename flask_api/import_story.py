from flask import Flask
from models import db, Story, Page, Choice
'''



     STORY FILE MADE BY AI (IDEA BY JAKUB AND TRISTAN)




'''
# --- Flask app setup ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://postgres:0000@localhost:5432/storyline")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
            "content": "Mohith wakes up early and prepares calmly. He grabs his student card and calculator.",
            "choices": [
                {"choice_text": "Take metro to EPITA", "next_page_key": "metro_good"},
            ]
        },
        {
            "page_key": "wake_up_late",
            "content": "Mohith overslept and is late. He forgot his calculator.",
            "choices": [
                {"choice_text": "Rush to EPITA anyway", "next_page_key": "metro_bad"},
            ]
        },
        {
            "page_key": "metro_good",
            "content": "The metro is smooth. You arrive early. No issues.",
            "is_ending": True
        },
        {
            "page_key": "metro_bad",
            "content": "On the metro, Mohith scrolls Instagram and misses his station. A random grandma gives him directions, but he's late.",
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
