import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

OLLAMA_URL = "http://localhost:11434/api/generate"

@api_view(['POST'])
def chat_with_phi3(request):
    # Get the message from the request body
    user_message = request.data.get("message")
    
    if not user_message:
        return Response({"error": "No message provided"}, status=400)
    
    payload = {
        "model": "phi3",
        "prompt": user_message,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()  # Raises error if status_code is 4xx/5xx
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Model request failed: {str(e)}"}, status=500)
    
    # Extract the model response
    result = response.json().get("response", "")
    
    return Response({"reply": result})

