from rest_framework import serializers

from backend.apps.notes.models import Note


class NoteSerializer(serializers.ModelSerializer):
    """Note Serializer"""

    class Meta:
        """Meta"""
        model = Note
        exclude = ['user']
