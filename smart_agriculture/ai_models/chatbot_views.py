import os
import logging
import google.generativeai as genai
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Configure Gemini API
logger = logging.getLogger('django')
genai.configure(api_key=settings.GEMINI_API_KEY)

# Define the model and system instruction
# We use gemini-1.5-flash as it is fast and supports system instructions well.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are the Smart Agriculture Platform AI Assistant. You help farmers manage crops, predict prices, and detect diseases. You can communicate fluently in any language the user speaks. Always be helpful, concise, and professional."
)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def api_chatbot(request):
    """
    API endpoint for the Multilingual AI Chatbot
    Requires a valid JWT token.
    Expects a JSON payload: {"message": "User's message here"}
    """
    if not settings.GEMINI_API_KEY:
         return Response(
            {'error': 'Chatbot API key not configured on the server.'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
    user_message = request.data.get('message')
    
    if not user_message:
        return Response(
            {'error': 'No message provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Generate the response
        response = model.generate_content(user_message)
        
        return Response({
            'message': response.text
        })
    except Exception as e:
        logger.error(f"DEBUG CHATBOT ERROR: {str(e)}")
        return Response(
            {'error': f'Failed to generate response: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
