from django.shortcuts import redirect
from django.contrib import messages
from game.flask_api import flask_api

def story_owner_required(view_func):
    def wrapper(request, story_id, *args, **kwargs):
        story = flask_api.get_story(story_id)
        if not story:
            messages.error(request, "Story not found.")
            return redirect('author_dashboard')
        
        
        if story.get('author_id') != request.user.id and not request.user.is_staff:
            messages.error(request, "You don't have permission to edit this story.")
            return redirect('author_dashboard')
        
        return view_func(request, story_id, *args, **kwargs)
    return wrapper