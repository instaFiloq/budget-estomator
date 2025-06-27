from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['project_id', 'address', 'user_id', 'created_at', 'messages']
        read_only_fields = ['user_id', 'created_at', 'messages']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']