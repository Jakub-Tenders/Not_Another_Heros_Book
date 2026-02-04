from flask import Blueprint, jsonify, abort
from models import (
    get_all_stories,
    get_story_by_id,
    get_start_page,
    get_page_by_id,
    get_choices_for_page,
    get_choice_by_id
)

api = Blueprint("api", __name__)


@api.route("/stories", methods=["GET"])
def stories():
    return jsonify(get_all_stories())


@api.route("/stories/<int:story_id>/start", methods=["GET"])
def story_start(story_id):
    story = get_story_by_id(story_id)
    if not story:
        abort(404)

    page = get_start_page(story_id)
    if not page:
        abort(404)

    choices = get_choices_for_page(page["id"])
    page["choices"] = choices

    return jsonify(page)


@api.route("/pages/<int:page_id>", methods=["GET"])
def get_page(page_id):
    page = get_page_by_id(page_id)
    if not page:
        abort(404)

    choices = get_choices_for_page(page_id)
    page["choices"] = choices

    return jsonify(page)


@api.route("/choices/<int:choice_id>", methods=["GET"])
def follow_choice(choice_id):
    choice = get_choice_by_id(choice_id)
    if not choice:
        abort(404)

    next_page_id = choice["to_page_id"]
    page = get_page_by_id(next_page_id)
    if not page:
        abort(404)

    choices = get_choices_for_page(next_page_id)
    page["choices"] = choices

    return jsonify(page)
