#-------------------- Imports -------------------#
#------------------------------------------------#
import json
import asyncio
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view,permission_classes,authentication_classes

from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AIImage
from .models import CustomUser
from .models import EmailAutomationAccount
from .models import Product
from .serializers import UserSerializer
from .agent import runner, session_service
from .email_automation import process_email_batch
from .auth import CookieJWTAuthentication
from .knowledge_base import (
    answer_from_knowledge_base,
    delete_knowledge_document,
    list_knowledge_documents,
    search_knowledge_base,
    upsert_knowledge_document,
)

# Get the custom user
User = get_user_model()

#---------- Signup View ---------#
#--------------------------------#
class Register(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        phone = request.data.get("phone")
        role = request.data.get("role", "User")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            role=role
        )

        return Response({
            "message": "Signup successful",
            "role": user.role
        }, status=201)


#------------Login View---------------#
#-------------------------------------#
from django.contrib.auth import get_user_model
User = get_user_model()
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=401)
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        role = user.role

        response = Response({
            "message": "Login Successful",
            "username": user.username,
            "email": user.email,
            "role": role,
            "success": True
        })

        # ---- FIXED: REMOVE domain="127.0.0.1" (breaks cookies on localhost) ----
        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
            max_age=3600
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
            max_age=7 * 24 * 3600
        )

        response.set_cookie(
        key="role",
        value=role,
        httponly=False,
        secure=True,
        samesite="None",
        path="/",
        )

        return response



#-------------------- Auth View ------------------#
#-------------------------------------------------#
class AuthCheck(APIView):
    def get(self, request):
        token = request.COOKIES.get("access_token")

        if not token:
            return Response({"authenticated": False})

        role = request.COOKIES.get("role")

        return Response({
            "authenticated": True,
            "role": role
        })





#--------------- Logout View --------------#
#------------------------------------------#
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"})
        # Remove access token cookie
        response.delete_cookie(
            key="access_token",
            path="/",
            samesite="None",
        )
        # Remove refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            path="/",
            samesite="None",
        )
        # Remove role cookie
        response.delete_cookie(
            key="role",
            path="/",
            samesite="None",
        )
        return response

#---------- AI Image Save View ---------#
#---------------------------------------#
@api_view(['POST'])
def save_ai_image(request):
    image_url = request.data.get('image_url')
    response = requests.get(image_url)
    if response.status_code == 200:
        file_name = "ai_gen_01.png"
        obj = AIImage()
        obj.image.save(file_name, ContentFile(response.content), save=True)
        return Response({"message": "Saved successfully!", "id": obj.id})
    return Response({"error": "Failed to fetch image"}, status=400)


#---------- Knowledge Base Views ---------#
#----------------------------------------#
@csrf_exempt
def knowledge_base_upload(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        title = (request.POST.get("title") or "").strip()
        preview = (request.POST.get("preview") or "").strip()
        uploaded_file = request.FILES.get("file")

        if not title and not uploaded_file:
            return JsonResponse({"error": "Title or file is required"}, status=400)

        file_bytes = uploaded_file.read() if uploaded_file else None
        filename = uploaded_file.name if uploaded_file else None

        result = upsert_knowledge_document(
            title=title or (uploaded_file.name if uploaded_file else "Knowledge Note"),
            file_bytes=file_bytes,
            filename=filename,
            preview_text=preview,
        )

        return JsonResponse({
            "message": "Knowledge base item indexed successfully",
            **result,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def knowledge_base_search(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    query = (request.GET.get("q") or "").strip()
    result = search_knowledge_base(query)
    return JsonResponse({
        "query": query,
        **result,
    })


@csrf_exempt
def knowledge_base_docs(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    return JsonResponse({
        "documents": list_knowledge_documents(),
    })


@csrf_exempt
def knowledge_base_delete(request, document_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        result = delete_knowledge_document(document_id)
        return JsonResponse({
            "message": "Knowledge base item deleted successfully",
            **result,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#---------- Chat Agent View ---------#
#------------------------------------#
import json
import os
import base64
import asyncio
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.genai.types import Content, Part
from openai import OpenAI
from .agent import get_agent, session_service, Runner  # Import from agent.py

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY"))


def _transcribe_audio(audio_base64):
    audio_data = base64.b64decode(audio_base64)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return transcript.text.strip()
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def _describe_frame(image_base64, prompt_text=""):
    prompt = prompt_text.strip() or "Describe the webcam frame and infer the user's intent."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"{prompt}\n"
                            "Return a concise, direct instruction or description that can be passed to an assistant."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                        },
                    },
                ],
            }
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def _resolve_input(data):
    user_audio_base64 = data.get("audio")
    user_image_base64 = data.get("image")
    user_text = (data.get("message") or "").strip()
    voice_enabled = bool(data.get("voice_enabled"))
    mode = "text"

    if user_audio_base64:
        user_text = _transcribe_audio(user_audio_base64)
        mode = "voice"

    if user_image_base64:
        frame_context = _describe_frame(user_image_base64, user_text)
        user_text = f"{user_text}\n\nVideo context: {frame_context}".strip() if user_text else frame_context
        if mode == "text":
            mode = "video"

    return user_text, mode, voice_enabled


def _answer_chat(user_text, mode):
    kb_answer, kb_result = answer_from_knowledge_base(user_text)
    if kb_answer:
        return kb_answer, kb_result, True

    agent = get_agent(mode=mode)
    runner = Runner(
        app_name="django_chat_app",
        agent=agent,
        session_service=session_service,
    )

    session_obj = asyncio.run(session_service.create_session(
        user_id="user_2",
        app_name="django_chat_app",
    ))

    formatted_msg = Content(role="user", parts=[Part(text=user_text)])
    events = runner.run(
        user_id="user_2",
        session_id=session_obj.id,
        new_message=formatted_msg,
    )

    final_response = ""
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text

    return final_response, kb_result, bool(kb_result.get("found"))


def _build_response_payload(response_text, user_text, mode, kb_result, voice_enabled=False):
    payload = {
        "response": response_text,
        "user_text": user_text,
        "mode_used": mode,
        "knowledge_base_used": bool(kb_result.get("found")),
        "knowledge_hits": kb_result.get("hits", []),
    }

    if voice_enabled:
        tts_res = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=response_text,
        )
        payload["audio_response"] = base64.b64encode(tts_res.content).decode("utf-8")

    return payload

@csrf_exempt
def chat_agent(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        user_text, mode, voice_enabled = _resolve_input(data)

        if not user_text:
            return JsonResponse({"error": "Empty message"}, status=400)

        response_text, kb_result, _ = _answer_chat(user_text, mode)
        return JsonResponse(_build_response_payload(
            response_text=response_text,
            user_text=user_text,
            mode=mode,
            kb_result=kb_result,
            voice_enabled=voice_enabled,
        ))

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def email_automation_run(request):
    try:
        account = EmailAutomationAccount.objects.filter(user=request.user).first()
        if not account:
            return Response(
                {"success": False, "error": "Email automation credentials are not saved"},
                status=400,
            )

        result = process_email_batch(
            email_account=account.email,
            app_password=account.app_password,
        )
        return Response(result)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def email_automation_config(request):
    account = EmailAutomationAccount.objects.filter(user=request.user).first()

    if request.method == "GET":
        if not account:
            return Response(
                {"email": "", "app_password": "", "is_reading": False}
            )

        return Response(
            {
                "email": account.email,
                "app_password": account.app_password,
                "is_reading": account.is_reading,
            }
        )

    email_value = (request.data.get("email") or "").strip()
    app_password = (request.data.get("app_password") or "").strip()
    is_reading = request.data.get("is_reading")

    if email_value or app_password:
        if not email_value or not app_password:
            return Response(
                {"success": False, "error": "Email and app password are required"},
                status=400,
            )

        if account:
            account.email = email_value
            account.app_password = app_password
            account.save()
        else:
            account = EmailAutomationAccount.objects.create(
                user=request.user,
                email=email_value,
                app_password=app_password,
            )

    if account and is_reading is not None:
        account.is_reading = bool(is_reading)
        account.save()

    return Response(
        {
            "success": True,
            "email": account.email,
            "app_password": account.app_password,
            "is_reading": account.is_reading,
        }
    )






    
#---------------- User List View ----------------#
#------------------------------------------------#
from .auth import CookieJWTAuthentication
class UserListView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "SuperAdmin":
            return Response({"error": "Forbidden"}, status=403)

        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    
#----------------- Edit User View -----------------#
#--------------------------------------------------#
@csrf_exempt
def update_user_view(request, id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error':'User not found'}, status=404)

    if request.method == 'GET':
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone
        }
        return JsonResponse(data)

    if request.method == 'PUT':
        data = json.loads(request.body)
        user.username = data.get('username')  # match frontend key
        user.email = data.get('email')
        user.phone = data.get('phone')
        user.save()
        return JsonResponse({'message':'User Updated Successfully'})

#---------------- Delete User View ---------------#
#-------------------------------------------------#
@csrf_exempt
def delete_user_view(request,id):
    user = CustomUser.objects.delete(id)
    user.delete()
    return JsonResponse("User Deleted Successfully")
    

# ---------------- Assign Role ---------------- #
# --------------------------------------------- #
@csrf_exempt
def set_role_view(request, id):
    if request.method != "PUT":
        return JsonResponse({"error": "Invalid method"}, status=405)
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    data = json.loads(request.body)
    role = data.get("role")
    if role not in ["User", "Admin", "SuperAdmin"]:
        return JsonResponse({"error": "Invalid role"}, status=400)
    user.role = role
    user.save()
    return JsonResponse({"message": "Role updated", "role": role})

#------------- Profile View -------------#
#----------------------------------------#
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .auth import CookieJWTAuthentication
from .serializers import UserSerializer

class ProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication]   # <-- ADDED
    permission_classes = [IsAuthenticated]               # <-- KEEP SAME

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response([serializer.data])               # SAME

    def patch(self, request):
        print(request.data)  # SAME
        user = request.user
        serializer = UserSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deleted"})

    

#-------------- Product List View -------------#
#----------------------------------------------#
def product_list(request):
    products = Product.objects.all()
    data = []
    for p in products:
        data.append({
            'id':p.id,
            'name':p.name,
            'price':p.price,
            'quantity':p.quantity,
            'description':p.description
        })
    return JsonResponse(data, safe=False)
    
#------------ Product Viewing View -------------#
#-----------------------------------------------#
def product_view(request, id):
    product = Product.objects.get(id=id)
    data = {
        'id':product.id,
        'name':product.name,
        'price':product.price,
        'quantity':product.quantity,
        'description':product.description
    }
    return JsonResponse(data)

#------------ Product Delete View -------------#
#----------------------------------------------#
@csrf_exempt
def product_del_view(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return JsonResponse('Product Deleted Successfully')

#------------- Product Update View -------------#
#-----------------------------------------------#
@csrf_exempt
def product_update_view(request, id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        product = Product.objects.get(id=id)
        product.name = data.get('name')
        product.price = data.get('price')
        product.quantity = data.get('quantity')
        product.description = data.get('description')
        product.save()
        return JsonResponse('Product Updated Successfully')

#---------------- Add Product View ---------------#
#-------------------------------------------------#
@csrf_exempt
def add_product_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(
            name = data.get('name'),
            price = data.get('price'),
            quantity = data.get('quantity'),
            description = data.get('description')
        )
        return JsonResponse({
            'message':'Product Added Successfully',
            'id':product.id
        })



