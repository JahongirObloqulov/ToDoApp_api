from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Todo
from .serializers import TodoSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsOwner
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.viewsets import ViewSet


# Create your views here.
class TodoListApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        print(request.user.id)
        todos = Todo.objects.all()
        # todos = Todo.objects.filter(user=request.user)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoDetailApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, todo_id):
        try:
            todo_instance = Todo.objects.get(id=todo_id)
            if todo_instance.user != self.request.user:
                todo_instance = None
        except Todo.DoesNotExist:
            todo_instance = None

        return todo_instance

    def get(self, request, todo_id, *args, **kwargs):
        todo_instance = self.get_object(todo_id)
        if not todo_instance:
            return Response({"error": "todo object doesnt find"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TodoSerializer(todo_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, todo_id, *args, **kwargs):
        todo_instance = self.get_object(todo_id)
        if not todo_instance:
            return Response({"error": "todo object doesn't find"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TodoSerializer(instance=todo_instance, data=request.data, context={'request': request})

        if todo_instance.user != request.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, todo_id, *args, **kwargs):
        todo_instance = self.get_object(todo_id)
        if not todo_instance:
            return Response({"error": "todo object doesnt find"}, status=status.HTTP_400_BAD_REQUEST)

        if todo_instance.user != request.user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)

        todo_instance.delete()
        return Response({"message": "To do deleted"})


class TodoViewSet(ViewSet):
    queryset = Todo.objects.all()

    def list(self, request, *args, **kwargs):
        serializer = TodoSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = TodoSerializer(item)
        return Response(serializer.data)

    def create(self, request):
        serializer = TodoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        todo_instance = get_object_or_404(self.queryset, pk=pk)

        serializer = TodoSerializer(instance=todo_instance, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        todo_instance = get_object_or_404(self.queryset, pk=pk)

        todo_instance.delete()
        return Response({"message": "To do deleted"})
