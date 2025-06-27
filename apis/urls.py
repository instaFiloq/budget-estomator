from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, TestViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('test/', TestViewSet.as_view(), name='test'),
    path('', include(router.urls)),
]