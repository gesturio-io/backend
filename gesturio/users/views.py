from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from django.contrib.auth.models import User
from django.http import JsonResponse
from .utils import generate_jwt_token,Autherize

class Login(APIView):
    
    @Autherize()
    def get(self,request,**kwargs):
        
        user = kwargs['user']
        return JsonResponse(
            {
                "id":user.id,
                "username":user.username,
                "email":user.email
            },
            status=200
        )
        
    def post(self,request):
        response = Response()
        try:
            username = request.data['email']
            password = request.data['password']
        except:
            response.data = {"status": "Incorrect input"}
            response.status_code = 404
            return response

        user = User.objects.filter(email=username)
        user = user.first()
        
        token = generate_jwt_token(user)
        refresh_token = generate_jwt_token(user,is_refresh=True)
           
        user.is_loggedin = True
        user.save()
        
        response.data ={
                    "id":user.id,
                    "email": user.email,
                    "status": 200,
                    "token":token,
                    "refresh_token":refresh_token
                    }
        response.status_code = 200
        response.set_cookie("jwt",token, httponly=True, secure=True, samesite="Lax")
        response.set_cookie("refresh_token",refresh_token, httponly=True, secure=True, samesite="Lax")
        
        return response