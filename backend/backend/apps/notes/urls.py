from django.urls import path

from backend.apps.notes.apps import NotesConfig
from backend.apps.notes.views import UserNoteListView, UserNoteView

app_name = NotesConfig.name

urlpatterns = [
    path('notes/', UserNoteListView.as_view(), name='user-note-list'),
    path('notes/<str:pk>/', UserNoteView.as_view(), name='user-note'),
]
