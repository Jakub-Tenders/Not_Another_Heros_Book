from django.urls import path
from game import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Gameplay
    path("play/<int:story_id>/", views.play_start, name="play_start"),
    path("play/session/<str:session_key>/", views.play_page, name="play_page"),
    path("play/session/<str:session_key>/choice/<int:choice_id>/", views.play_choice, name="play_choice"),
    path("play/<int:story_id>/restart/", views.play_restart, name="play_restart"),

    # Author tools
    path("author/", views.author_dashboard, name="author_dashboard"),
    path("author/stories/create/", views.author_story_create, name="author_story_create"),
    path("author/stories/<int:story_id>/edit/", views.author_story_edit, name="author_story_edit"),
    path("author/stories/<int:story_id>/delete/", views.author_story_delete, name="author_story_delete"),
    path("author/stories/<int:story_id>/pages/create/", views.author_page_create, name="author_page_create"),
    path("author/pages/<int:page_id>/edit/", views.author_page_edit, name="author_page_edit"),
    path("author/pages/<int:page_id>/delete/", views.author_page_delete, name="author_page_delete"),
    path("author/pages/<int:page_id>/choices/create/", views.author_choice_create, name="author_choice_create"),
    path("author/choices/<int:choice_id>/delete/", views.author_choice_delete, name="author_choice_delete"),
]