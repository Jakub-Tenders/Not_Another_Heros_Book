from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tags = db.Column(db.String(500), nullable=True)
    author_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="published")
    start_page_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "author_name": self.author_name,
            "status": self.status,
            "start_page_id": self.start_page_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey("story.id"), nullable=False)
    page_key = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_start = db.Column(db.Boolean, default=False)
    is_ending = db.Column(db.Boolean, default=False)
    ending_label = db.Column(db.String(100), nullable=True)
    page_number = db.Column(db.Integer)
    extradata = db.Column(db.JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "story_id": self.story_id,
            "page_key": self.page_key,
            "content": self.content,
            "is_start": self.is_start,
            "is_ending": self.is_ending,
            "page_number": self.page_number,
            "extradata": self.extradata
        }


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_page_id = db.Column(db.Integer, db.ForeignKey("page.id"), nullable=False)
    to_page_id = db.Column(db.Integer, db.ForeignKey("page.id"), nullable=False)
    choice_text = db.Column(db.String(500), nullable=False)
    choice_order = db.Column(db.Integer, default=0)
    time_change = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "from_page_id": self.from_page_id,
            "to_page_id": self.to_page_id,
            "choice_text": self.choice_text,
            "choice_order": self.choice_order,
            "time_change": self.time_change
        }
