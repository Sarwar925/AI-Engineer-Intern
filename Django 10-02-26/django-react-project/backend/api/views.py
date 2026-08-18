from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import traceback
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Profile
from .serializers import UserSerializer

# ---------------- SIGNUP ----------------
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'msg': 'User created'})
    return Response(serializer.errors)

# ---------------- LOGIN ----------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user:
        # 🔥 clear any old sessions and start fresh
        django_logout(request)
        request.session.flush()

        django_login(request, user)     # create new session
        request.session.save()          # persist immediately

        return Response({
            "msg": "Login success",
            "username": user.username,
            "id": user.id,
            "sessionid": request.session.session_key,  # for debugging
        })
    return Response({"msg": "Invalid credentials"}, status=401)

# ---------------- LOGOUT ----------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    django_logout(request)
    request.session.flush()   # optional safety reset
    return Response({"msg": "Logout success"})


# ---------------- GET USERS ----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    data = []
    for u in users:
        phone = ""
        if hasattr(u, 'profile'):
            phone = u.profile.phone
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "phone": phone
        })
    return Response(data)


# ---------------- CREATE USER ----------------
@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'msg': 'User added'})
    return Response(serializer.errors)

# ---------------- UPDATE USER ----------------
@api_view(['PUT'])
def update_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'msg': 'User not found'})

    user.username = request.data.get('username', user.username)
    user.email = request.data.get('email', user.email)

    if request.data.get('password'):
        user.set_password(request.data['password'])

    user.save()

    if hasattr(user, 'profile'):
        user.profile.phone = request.data.get('phone', user.profile.phone)
        user.profile.save()

    return Response({'msg': 'User updated'})

# ---------------- DELETE USER ----------------
@api_view(['DELETE'])
def delete_user(request, id):
    try:
        user = User.objects.get(id=id)
        user.delete()
        return Response({'msg': 'User deleted'})
    except User.DoesNotExist:
        return Response({'msg': 'User not found'})









import json
import sys
import logging
import os
import dotenv
import traceback # Added for better debugging

from django.http import JsonResponse
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Profile
from .serializers import UserSerializer

# Google ADK / AI Imports
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import LiteLlm

# --- LOGGING & ENVIRONMENT ---
dotenv.load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("django_agent")

# --- AI SETUP WITH ERROR HANDLING ---
OPENAI_KEY = os.environ.get("OPENAI_KEY")

global_session_service = InMemorySessionService()

# Initialize variables as None first to prevent crash on import
openai_model = None
root_agent = None

if not OPENAI_KEY:
    logger.error("❌ CRITICAL: OPENAI_KEY not found in environment variables!")
else:
    try:
        openai_model = LiteLlm(model="openai/gpt-4o", api_key=OPENAI_KEY)
        root_agent = LlmAgent(
            model=openai_model, 
            name="social_assistant", 
            instruction="You are a helpful social media assistant."
        )
        logger.info("✅ AI Agent initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI Agent: {e}")

class UserMessage:
    def __init__(self, content):
        self.role = "user"
        self.content = content

# ---------------- AUTH & USER CRUD ----------------
# (Your signup, login_view, logout_view, etc. remain the same as they were working)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'msg': 'User created successfully', 'username': user.username})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user:
        django_login(request, user)
        return Response({
            "msg": "Login success",
            "username": user.username,
            "id": user.id,
            "sessionid": request.session.session_key,  # debug
        })
    return Response({"msg": "Invalid credentials"}, status=401)

# ... (Include get_users, update_user, delete_user here) ...

# ---------------- AI AGENT VIEW ----------------

@csrf_exempt
def agent_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required. Please login first."}, status=401)

    # Check if agent was actually initialized
    if root_agent is None:
        return JsonResponse({"error": "AI Agent is not configured. Check server logs for API Key errors."}, status=500)

    try:
        data = json.loads(request.body)
        user_msg_text = data.get("message", "")

        session_id = f"session_user_{request.user.id}"

        if not global_session_service.has_session(session_id):
            global_session_service.create_session(session_id=session_id)

        formatted_message = UserMessage(user_msg_text)

        runner = Runner(
            agent=root_agent, 
            session_service=global_session_service, 
            app_name="social_media_app"
        )

        agent_reply = ""
        # runner.run is often a generator, so we iterate through events
        events = runner.run(
            user_id=str(request.user.id), 
            session_id=session_id, 
            new_message=formatted_message
        )

        for event in events:
            # Safely navigate the event object
            payload = getattr(event, "content", getattr(event, "message", None))
            if payload and hasattr(payload, "parts"):
                for part in payload.parts:
                    if hasattr(part, "text") and part.text:
                        agent_reply += part.text

        return JsonResponse({
            "reply": agent_reply if agent_reply else "Agent processed but returned no text.",
            "user": request.user.username
        })

    except Exception as e:
        # This will print the full traceback to your terminal so you can see the REAL error
        logger.error("Error in agent_chat:")
        traceback.print_exc() 
        return JsonResponse({"error": str(e)}, status=500)