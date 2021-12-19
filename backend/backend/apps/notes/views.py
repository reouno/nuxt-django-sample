from django.http import Http404
from rest_framework import permissions, status
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.notes.models import Note
from backend.apps.notes.serializers import NoteSerializer


class UserNoteListView(APIView):
    """User note list view"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List all notes owned by request user"""
        user = self.request.user
        notes = Note.objects.filter(user=user)

        return Response({'notes': NoteSerializer(notes, many=True).data}, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new note"""
        user = self.request.user
        serializer = NoteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({'errors': ['Invalid fields'], 'detail': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        note = Note.objects.create(user=user, content=serializer.validated_data['content'])
        note.save()

        return Response(NoteSerializer(note).data, status=status.HTTP_201_CREATED)


class UserNoteView(APIView):
    """User note view"""
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get_and_validate(pk, user):
        """Try to get course object"""
        try:
            note = Note.objects.get(pk=pk)
        except Note.DoesNotExist as no_exist:
            raise Http404 from no_exist

        # return 404 when the specified course is not owned by the request user
        if note.user != user:
            raise Http404

        return note

    def get(self, request, pk):
        """Get note by ID"""
        note = self.get_and_validate(pk, self.request.user)

        return Response({'note': NoteSerializer(note).data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Update note"""
        note = self.get_and_validate(pk, self.request.user)
        serializer = NoteSerializer(note, data=request.data)
        if not serializer.is_valid():
            return Response({'errors': ['Invalid fields'], 'detail': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({'note': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete note by ID"""
        note = self.get_and_validate(pk, self.request.user)
        note.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
