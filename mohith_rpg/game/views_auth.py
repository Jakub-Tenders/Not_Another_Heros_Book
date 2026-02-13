from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from game.models import UserProfile, Report
from game.flask_api import flask_api

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='reader')
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    """User profile page"""
    return render(request, 'registration/profile.html')

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

@staff_member_required
def admin_unsuspend_story(request, story_id):
    """Unsuspend a story"""
    if request.method == 'POST':
        flask_api.update_story(story_id, status='published')
        messages.success(request, "Story unsuspended.")
    return redirect('admin_stories')

@staff_member_required
def admin_reports_view(request):
    """Admin view all reports"""
    reports = Report.objects.all().order_by('-id')
    return render(request, 'admin/reports.html', {'reports': reports})

@staff_member_required
def admin_review_report(request, report_id):
    """Review and resolve a report"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('moderator_notes', '')
        
        if action == 'suspend':
            flask_api.update_story(report.story_id, status='suspended')
            report.status = 'resolved'
        elif action == 'dismiss':
            report.status = 'dismissed'
        
        report.moderator_notes = notes
        report.reviewed_by = request.user
        report.save()
        
        messages.success(request, "Report reviewed.")
        return redirect('admin_reports')
    
    story = flask_api.get_story(report.story_id)
    return render(request, 'admin/report_review.html', {
        'report': report,
        'story': story
    })