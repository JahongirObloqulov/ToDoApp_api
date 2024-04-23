from django.urls import path, include
from rest_framework import routers

from .views import TodoListApiView, TodoDetailApiView, TodoViewSet

router = routers.DefaultRouter()
router.register(r'api-viewset', TodoViewSet)

urlpatterns = [
    path('api/', TodoListApiView.as_view()),
    path('api/<int:todo_id>/', TodoDetailApiView.as_view()),
    path('', include(router.urls))
]
