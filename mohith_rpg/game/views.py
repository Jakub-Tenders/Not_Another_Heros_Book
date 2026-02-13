from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from game.flask_api import flask_api
from game.models import PlaySession, Play
import uuid
from django.contrib.auth.decorators import login_required
from game.decorators import story_owner_required


# ─────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────

def home(request):
    """List all published stories."""
    search = request.GET.get("search", "")
    stories = flask_api.get_stories(status="published", search=search or None)
    return render(request, "home.html", {
        "stories": stories,
        "search": search,
    })


# ─────────────────────────────────────────
#  GAMEPLAY
# ─────────────────────────────────────────

def play_start(request, story_id):
    """Start or resume a story."""
    story = flask_api.get_story(story_id)
    if not story:
        messages.error(request, "Story not found.")
        return redirect("home")

    if not story.get("start_page_id"):
        messages.error(request, "This story has no starting page yet.")
        return redirect("home")

    # Create a new session
    session_key = str(uuid.uuid4())
    start_page_id = story["start_page_id"]

    PlaySession.objects.create(
        session_key=session_key,
        story_id=story_id,
        current_page_id=start_page_id,
        user=request.user if request.user.is_authenticated else None,
    )

    return redirect("play_page", session_key=session_key)


def play_page(request, session_key):
    """Display the current page of a play session."""
    session = PlaySession.objects.filter(session_key=session_key).first()
    if not session:
        messages.error(request, "Session not found.")
        return redirect("home")

    page = flask_api.get_page(session.current_page_id)
    if not page:
        messages.error(request, "Page not found.")
        return redirect("home")

    story = flask_api.get_story(session.story_id)

    # If it's an ending, record a completed play
    if page.get("is_ending"):
        Play.objects.get_or_create(
            story_id=session.story_id,
            ending_page_id=page["id"],
            user=request.user if request.user.is_authenticated else None,
            defaults={'created_at': timezone.now()}
        )

    return render(request, "play.html", {
        "session": session,
        "page": page,
        "story": story,
        "choices": page.get("choices", []),
        "is_ending": page.get("is_ending", False),
    })


def play_choice(request, session_key, choice_id):
    """Handle a choice - advance session to next page."""
    if request.method != "POST":
        return redirect("play_page", session_key=session_key)

    session = PlaySession.objects.filter(session_key=session_key).first()
    if not session:
        messages.error(request, "Session not found.")
        return redirect("home")

    # Get current page to find the choice
    page = flask_api.get_page(session.current_page_id)
    if not page:
        return redirect("home")

    # Find the chosen choice
    chosen = next((c for c in page.get("choices", []) if c["id"] == choice_id), None)
    if not chosen:
        messages.error(request, "Invalid choice.")
        return redirect("play_page", session_key=session_key)

    # Advance session to next page
    session.current_page_id = chosen["next_page_id"]
    session.save()

    return redirect("play_page", session_key=session_key)


def play_restart(request, story_id):
    """Restart a story from the beginning."""
    return redirect("play_start", story_id=story_id)


# ─────────────────────────────────────────
#  AUTHOR TOOLS
# ─────────────────────────────────────────

@login_required
def author_dashboard(request):
    """List all stories for authoring."""
    stories = flask_api.get_stories()
    user_stories = [s for s in stories if s.get('author_id') == request.user.id]
    return render(request, 'author/dashboard.html', {'stories': user_stories})

@login_required
def author_story_create(request):
    """Create a new story."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status", "draft")
        tags = request.POST.get("tags", "").strip()

        if not title:
            messages.error(request, "Title is required.")
            return render(request, "author/story_form.html", {
                "action": "Create",
                "story": request.POST,
            })

        story = flask_api.create_story(
            title=title,
            description=description,
            status=status,
            tags=tags if tags else None,
            author_id=request.user.id
        )

        if story:
            messages.success(request, f"Story '{story['title']}' created!")
            return redirect("author_story_edit", story_id=story["id"])
        else:
            messages.error(request, "Failed to create story. Please try again.")

    return render(request, "author/story_form.html", {
        "action": "Create",
        "story": {},
    })

@login_required
@story_owner_required
def author_story_edit(request, story_id):
    """Edit an existing story's metadata and manage its pages."""
    story = flask_api.get_story(story_id, include_pages=True)
    if not story:
        messages.error(request, "Story not found.")
        return redirect("author_dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        status = request.POST.get("status", "draft")
        tags = request.POST.get("tags", "").strip()

        if not title:
            messages.error(request, "Title is required.")
        else:
            updated = flask_api.update_story(
                story_id,
                title=title,
                description=description,
                status=status,
                tags=tags if tags else None,
            )
            if updated:
                messages.success(request, "Story updated!")
                story = flask_api.get_story(story_id, include_pages=True)
            else:
                messages.error(request, "Failed to update story.")

    return render(request, "author/story_edit.html", {"story": story})

@login_required
@story_owner_required
def author_story_delete(request, story_id):
    """Delete a story."""
    if request.method == "POST":
        success = flask_api.delete_story(story_id)
        if success:
            messages.success(request, "Story deleted.")
        else:
            messages.error(request, "Failed to delete story.")
    return redirect("author_dashboard")

@login_required
@story_owner_required
def author_page_create(request, story_id):
    """Add a new page to a story."""
    story = flask_api.get_story(story_id)
    if not story:
        messages.error(request, "Story not found.")
        return redirect("author_dashboard")

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        is_ending = request.POST.get("is_ending") == "on"
        ending_label = request.POST.get("ending_label", "").strip()

        if not text:
            messages.error(request, "Page text is required.")
        else:
            page = flask_api.create_page(
                story_id=story_id,
                text=text,
                is_ending=is_ending,
                ending_label=ending_label if ending_label else None,
            )
            if page:
                messages.success(request, "Page created!")
                return redirect("author_story_edit", story_id=story_id)
            else:
                messages.error(request, "Failed to create page.")

    return render(request, "author/page_form.html", {
        "action": "Create",
        "story": story,
        "page": {},
    })

@login_required
def author_page_edit(request, page_id):
    """Edit an existing page."""
    page = flask_api.get_page(page_id)
    if not page:
        messages.error(request, "Page not found.")
        return redirect("author_dashboard")

    story = flask_api.get_story(page["story_id"], include_pages=True)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        is_ending = request.POST.get("is_ending") == "on"
        ending_label = request.POST.get("ending_label", "").strip()

        if not text:
            messages.error(request, "Page text is required.")
        else:
            updated = flask_api.update_page(
                page_id,
                text=text,
                is_ending=is_ending,
                ending_label=ending_label if ending_label else None,
            )
            if updated:
                messages.success(request, "Page updated!")
                page = flask_api.get_page(page_id)
            else:
                messages.error(request, "Failed to update page.")

    return render(request, "author/page_form.html", {
        "action": "Edit",
        "story": story,
        "page": page,
    })

@login_required
def author_page_delete(request, page_id):
    """Delete a page."""
    page = flask_api.get_page(page_id)
    story_id = page["story_id"] if page else None

    if request.method == "POST":
        success = flask_api.delete_page(page_id)
        if success:
            messages.success(request, "Page deleted.")
        else:
            messages.error(request, "Failed to delete page.")

    if story_id:
        return redirect("author_story_edit", story_id=story_id)
    return redirect("author_dashboard")

@login_required
def author_choice_create(request, page_id):
    """Add a choice to a page."""
    page = flask_api.get_page(page_id)
    if not page:
        messages.error(request, "Page not found.")
        return redirect("author_dashboard")

    story = flask_api.get_story(page["story_id"], include_pages=True)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        next_page_id = request.POST.get("next_page_id")

        if not text or not next_page_id:
            messages.error(request, "Choice text and destination page are required.")
        else:
            choice = flask_api.create_choice(
                page_id=page_id,
                text=text,
                next_page_id=int(next_page_id),
            )
            if choice:
                messages.success(request, "Choice added!")
                return redirect("author_page_edit", page_id=page_id)
            else:
                messages.error(request, "Failed to create choice.")

    return render(request, "author/choice_form.html", {
        "page": page,
        "story": story,
        "all_pages": story.get("pages", []),
    })

@login_required
def author_choice_delete(request, choice_id):
    """Delete a choice."""
    # We need page_id to redirect back - pass it as POST data
    page_id = request.POST.get("page_id")

    if request.method == "POST":
        success = flask_api.delete_choice(choice_id)
        if success:
            messages.success(request, "Choice deleted.")
        else:
            messages.error(request, "Failed to delete choice.")

    if page_id:
        return redirect("author_page_edit", page_id=page_id)
    return redirect("author_dashboard")
