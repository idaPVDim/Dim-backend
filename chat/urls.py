from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, MessageNotificationViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'notifications', MessageNotificationViewSet, basename='chat-notification')

urlpatterns = router.urls
