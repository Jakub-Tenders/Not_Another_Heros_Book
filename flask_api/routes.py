from flask import Blueprint, jsonify, request, abort
from models import db, Story, Page, Choice

api = Blueprint("api", __name__)

# ----------------------- Stories -----------------------------
@api.route("/stories", methods=["GET"])
def stories():
    status = request.args.get("status")
    if status:
        stories = Story.query.filter_by(status=status).order_by(Story.created_at.desc()).all()
    else:
        stories = Story.query.order_by(Story.created_at.desc()).all()
    return jsonify([s.to_dict() for s in stories])



@api.route("/stories/<int:story_id>", methods=["GET"])
def get_story(story_id):
    story = Story.query.get_or_404(story_id)
    return jsonify(story.to_dict())



@api.route("/stories", methods=["POST"])
def create_new_story():
    data = request.get_json()
    if not data or not data.get("title") or not data.get("author_name"):
        return jsonify({"error": "title and author_name required"}), 400
    story = Story(
        title=data["title"],
        description=data.get("description", ""),
        author_name=data["author_name"],
        status=data.get("status", "published")
    )
    db.session.add(story)
    db.session.commit()
    return jsonify(story.to_dict()), 201



@api.route("/stories/<int:story_id>", methods=["PUT"])
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    for key in ["title", "description", "author_name", "status"]:
        if key in data:
            setattr(story, key, data[key])
    db.session.commit()
    return jsonify(story.to_dict())



@api.route("/stories/<int:story_id>", methods=["DELETE"])
def remove_story(story_id):
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    return jsonify({"message": "Story deleted"}), 200



# ---------------------- Pages -----------------------------
@api.route("/stories/<int:story_id>/start", methods=["GET"])
def story_start(story_id):
    story = Story.query.get_or_404(story_id)
    page = Page.query.get_or_404(story.start_page_id)
    choices = Choice.query.filter_by(from_page_id=page.id).order_by(Choice.choice_order).all()
    page_dict = page.to_dict()
    page_dict["choices"] = [c.to_dict() for c in choices]
    return jsonify(page_dict)



@api.route("/stories/<int:story_id>/pages", methods=["POST"])
def add_page_to_story(story_id):
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    if not data or not data.get("page_key") or not data.get("content"):
        return jsonify({"error": "page_key and content required"}), 400
    page = Page(
        story_id=story_id,
        page_key=data["page_key"],
        content=data["content"],
        is_start=data.get("is_start", False),
        is_ending=data.get("is_ending", False)
    )
    db.session.add(page)
    db.session.commit()
    return jsonify(page.to_dict()), 201



@api.route("/pages/<int:page_id>", methods=["GET"])
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    choices = Choice.query.filter_by(from_page_id=page.id).order_by(Choice.choice_order).all()
    page_dict = page.to_dict()
    page_dict["choices"] = [c.to_dict() for c in choices]
    return jsonify(page_dict)


@api.route("/pages/<int:page_id>", methods=["PUT"])
def edit_page(page_id):
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    for key in ["content", "is_start", "is_ending"]:
        if key in data:
            setattr(page, key, data[key])
    db.session.commit()
    return jsonify(page.to_dict())

@api.route("/pages/<int:page_id>", methods=["DELETE"])
def remove_page(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return jsonify({"message": "Page deleted"}), 200



# --------------------------- Choices ------------------------------
@api.route("/pages/<int:page_id>/choices", methods=["POST"])
def add_choice_to_page(page_id):
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    if not data or not data.get("to_page_id") or not data.get("choice_text"):
        return jsonify({"error": "to_page_id and choice_text required"}), 400
    to_page = Page.query.get_or_404(data["to_page_id"])
    choice = Choice(
        from_page_id=page.id,
        to_page_id=to_page.id,
        choice_text=data["choice_text"],
        choice_order=data.get("choice_order", 0)
    )
    db.session.add(choice)
    db.session.commit()
    return jsonify(choice.to_dict()), 201


@api.route("/choices/<int:choice_id>", methods=["GET"])
def follow_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    page = Page.query.get_or_404(choice.to_page_id)
    choices = Choice.query.filter_by(from_page_id=page.id).order_by(Choice.choice_order).all()
    page_dict = page.to_dict()
    page_dict["choices"] = [c.to_dict() for c in choices]
    return jsonify(page_dict)


@api.route("/choices/<int:choice_id>", methods=["PUT"])
def edit_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    for key in ["choice_text", "choice_order"]:
        if key in data:
            setattr(choice, key, data[key])
    db.session.commit()
    return jsonify(choice.to_dict())


@api.route("/choices/<int:choice_id>", methods=["DELETE"])
def remove_choice(choice_id):
    choice = Choice.query.get_or_404(choice_id)
    db.session.delete(choice)
    db.session.commit()
    return jsonify({"message": "Choice deleted"}), 200
