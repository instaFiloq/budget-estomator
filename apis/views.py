from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, MessageCreateSerializer
from .utils import get_chat_response, get_estimated_budget_response
import json

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = self.get_object()
            instance.delete()
        except:
            print("new conversation!")
            
        self.perform_create(serializer)
        startingMessage = "Welcome, i'm a fix and flip projects expert i can help you estimate your project budget. Please start by describing the property you are planing to flip."
        # Create welcome message
        conversation = serializer.instance
        Message.objects.create(
            conversation=conversation,
            content=startingMessage,
            role='assistant'
        )
        
        return Response(
            {"message": startingMessage},
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        return Conversation.objects.filter(user_id=self.request.user.user_id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.user_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        try:
            pId=self.kwargs['pk'] if self.kwargs['pk'] else None
            return Conversation.objects.get(
                pk=pId,
                user_id=self.request.user.user_id
            )
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found")

    @action(detail=True, methods=['post'], serializer_class=MessageCreateSerializer)
    def messages(self, request, pk=None):
        conversation = self.get_object()
        
        prompt = request.data['content']
        
        # Prepare chat history
        messages = conversation.messages.all().order_by('created_at')
        chat_history = [{
            "role": msg.role,
            "content": msg.content
        } for msg in messages]

        chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Get bot response
            bot_response = get_chat_response(chat_history)

            # Save user message
            Message.objects.create(
                conversation=conversation,
                content=prompt,
                role='user'
            )
            
            # Save bot message
            Message.objects.create(
                conversation=conversation,
                content=bot_response,
                role='assistant'
            )
            
            return Response({"message": bot_response}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def budget(self, request, pk=None):
        conversation = self.get_object()

        messages = conversation.messages.all().order_by('created_at')
        chat_history = [{
            "role": msg.role,
            "content": msg.content
        } for msg in messages]
        
        # return Response({"history": chat_history})
        try:
            budget = get_estimated_budget_response(chat_history)
            
            return Response({"budget": json.loads(budget)})
            
        except Exception as e:
            print(e)
            return Response(
                {"error": f"Failed to generate budget: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )