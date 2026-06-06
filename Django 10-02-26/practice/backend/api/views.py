from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class SignupView(APIView):

    def post(self,request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Signup Successful"})

        return Response(serializer.errors)



class LoginView(APIView):

    def post(self,request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email,password=password)
            refresh = RefreshToken.for_user(user)
            return Response({
                "access":str(refresh.access_token),
                "refresh":str(refresh)
            })
        
        except:
            return Response({"error":"Invalid Credentials"},status=401)