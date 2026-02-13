from flask import Blueprint, jsonify, request, abort, current_app
from models import db, Story, Page, Choice

api = Blueprint("api", __name__)


def require_api_key():
    """Check API key for write operations"""
    expected = current_app.config.get("API_KEY", "")
    if not expected:
        return None  # If no key is configured, allow access
    
    provided = request.headers.get("X-API-KEY", "")
    if provided != expected:
        return jsonify({"error": "Invalid or missing API key"}), 401
    return None



@api.route("/stories", methods=["GET"])
def stories():

    status = request.args.get("status")
    search = request.args.get("search")
    tags = request.args.get("tags")
    
    query = Story.query
    
    if status:
        query = query.filter_by(status=status)
    

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Story.title.ilike(like_pattern),
                Story.description.ilike(like_pattern)
            )
        )
    

    if tags:
        tag_pattern = f"%{tags}%"
        query = query.filter(Story.tags.ilike(tag_pattern))
    
    stories_list = query.order_by(Story.created_at.desc()).all()
    return jsonify([s.to_dict() for s in stories_list])


@api.route("/stories/<int:story_id>", methods=["GET"])
def get_story(story_id):

    story = Story.query.get_or_404(story_id)
    result = story.to_dict()
    

    include_pages = request.args.get("include_pages", "").lower() in ["1", "true", "yes"]
    
    if include_pages:
        pages = Page.query.filter_by(story_id=story_id).order_by(Page.id).all()
        result["pages"] = []
        
        for idx, page in enumerate(pages, start=1):
            page_dict = page.to_dict()
            page_dict["page_number"] = idx  
            
            # Get choices for this page
            choices = Choice.query.filter_by(from_page_id=page.id).order_by(Choice.choice_order).all()
            page_dict["choices"] = [c.to_dict() for c in choices]
            
            result["pages"].append(page_dict)
    
    return jsonify(result)


@api.route("/stories", methods=["POST"])
def create_new_story():
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    
    story = Story(
        title=data["title"],
        description=data.get("description", ""),
        author_name=data.get("author_name", "Anonymous"),
        author_id=data.get("author_id"),
        status=data.get("status", "published"),
        tags=data.get("tags", "")
    )
    db.session.add(story)
    db.session.commit()
    return jsonify(story.to_dict()), 201


@api.route("/stories/<int:story_id>", methods=["PUT"])
def edit_story(story_id):
    
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    
    for key in ["title", "description", "author_name", "author_id", "status", "tags", "start_page_id"]:
        if key in data:
            setattr(story, key, data[key])
    
    db.session.commit()
    return jsonify(story.to_dict())


@api.route("/stories/<int:story_id>", methods=["DELETE"])
def remove_story(story_id):
    
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    story = Story.query.get_or_404(story_id)
    
    
    pages = Page.query.filter_by(story_id=story_id).all()
    page_ids = [p.id for p in pages]
    
   
    if page_ids:
        Choice.query.filter(Choice.from_page_id.in_(page_ids)).delete(synchronize_session=False)
    
   
    Page.query.filter_by(story_id=story_id).delete(synchronize_session=False)
    
   
    db.session.delete(story)
    db.session.commit()
    
    return jsonify({"message": "Story deleted", "deleted": True}), 200



@api.route("/stories/<int:story_id>/start", methods=["GET"])
def story_start(story_id):
   
    story = Story.query.get_or_404(story_id)
    
    if not story.start_page_id:
        return jsonify({"error": "start_page_id not set"}), 400
    
    page = Page.query.get_or_404(story.start_page_id)
    choices = Choice.query.filter_by(from_page_id=page.id).order_by(Choice.choice_order).all()
    
    page_dict = page.to_dict()
    page_dict["choices"] = [c.to_dict() for c in choices]
    
    return jsonify({"page_id": page.id})


@api.route("/stories/<int:story_id>/pages", methods=["POST"])
def add_page_to_story(story_id):
    
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    story = Story.query.get_or_404(story_id)
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"error": "content is required"}), 400
    
    page = Page(
        story_id=story_id,
        page_key=data.get("page_key", f"page_{db.session.query(db.func.count(Page.id)).filter_by(story_id=story_id).scalar() + 1}"),
        content=data["content"],
        is_start=data.get("is_start", False),
        is_ending=data.get("is_ending", False),
        ending_label=data.get("ending_label")
    )
    db.session.add(page)
    db.session.commit()
    
    
    if not story.start_page_id:
        story.start_page_id = page.id
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
   
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
   
    for key in ["content", "is_start", "is_ending", "ending_label", "page_key"]:
        if key in data:
            setattr(page, key, data[key])
    
    db.session.commit()
    return jsonify(page.to_dict())


@api.route("/pages/<int:page_id>", methods=["DELETE"])
def remove_page(page_id):

    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    page = Page.query.get_or_404(page_id)
    
    
    Choice.query.filter_by(from_page_id=page.id).delete(synchronize_session=False)
    
    
    story = Story.query.get(page.story_id)
    if story and story.start_page_id == page.id:
        story.start_page_id = None
    
    db.session.delete(page)
    db.session.commit()
    
    return jsonify({"message": "Page deleted", "deleted": True}), 200


@api.route("/pages/<int:page_id>/choices", methods=["POST"])
def add_choice_to_page(page_id):
   
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    page = Page.query.get_or_404(page_id)
    data = request.get_json()
    
    if not data or not data.get("to_page_id") or not data.get("choice_text"):
        return jsonify({"error": "to_page_id and choice_text required"}), 400
    
    to_page = Page.query.get_or_404(data["to_page_id"])
    
    
    if page.story_id != to_page.story_id:
        return jsonify({"error": "Both pages must belong to the same story"}), 400
    
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
    
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    choice = Choice.query.get_or_404(choice_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
   
    for key in ["choice_text", "choice_order", "to_page_id"]:
        if key in data:
            
            if key == "to_page_id":
                to_page = Page.query.get_or_404(data[key])
                from_page = Page.query.get(choice.from_page_id)
                if from_page.story_id != to_page.story_id:
                    return jsonify({"error": "Pages must belong to the same story"}), 400
            
            setattr(choice, key, data[key])
    
    db.session.commit()
    return jsonify(choice.to_dict())


@api.route("/choices/<int:choice_id>", methods=["DELETE"])
def remove_choice(choice_id):
    
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    
    choice = Choice.query.get_or_404(choice_id)
    db.session.delete(choice)
    db.session.commit()
    
    return jsonify({"message": "Choice deleted", "deleted": True}), 200


def health():
    return jsonify({"status": "ok"})