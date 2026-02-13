from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from game.models import UserProfile
from django.contrib.admin.views.decorators import staff_member_required
from game.flask_api import flask_api
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile with default role
            UserProfile.objects.create(user=user, role='reader')
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@staff_member_required
def admin_stories_view(request):
    """Admin can see all stories and suspend them"""
    stories = flask_api.get_stories()
    return render(request, 'admin/stories.html', {'stories': stories})

@staff_member_required
def admin_suspend_story(request, story_id):
    """Suspend a story"""
    if request.method == 'POST':
        flask_api.update_story(story_id, status='suspended')
        messages.success(request, "Story suspended.")
    return redirect('admin_stories')