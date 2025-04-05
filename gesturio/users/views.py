from django.conf import settings
from django.shortcuts import redirect
from .serializers import RegisterSerializer, UpdateProfileSerializer, LoginSerializer, EmailVerificationRequestSerializer, EmailVerificationSerializerOTPCheck
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import UserAuth, UserProfile, LoginType
from django.http import JsonResponse
from .utils import generate_jwt_token,Autherize,otp_set_and_gen,send_email
from .password_utils import verify_hash,generate_hash
from django.core.exceptions import ValidationError
from django.core.cache import cache

def index(request):
    # print(request.META["HTTP_X_FORWARDED_PROTO"])
    return JsonResponse({'message': 'Hello, World!'})


def cache_test(request):
    cache.set('test', 'Hello, World!', timeout=60)
    return JsonResponse({'message': str(cache.get('test'))})


def get_ip_address(request):
     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
     print(settings.BASE_DIR)
     if x_forwarded_for:
        ip_list = [ip.strip() for ip in x_forwarded_for.split(',')]
     else:
        ip_list = [request.META.get('REMOTE_ADDR')]
     return JsonResponse({'ip': ip_list})


class RegisterAuth(APIView):
    def post(self,request):
        response = Response()
        try:
            
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save(
                    login_type=LoginType.email,
                    email_verified=False
                )
                response.data = {
                    "status": "success",
                    "message": "User registered successfully"
                }
                response.status_code = 201 # CREATED 
                return response
            
            else:
                response.data = serializer.errors
                response.status_code = 400  # BAD REQUEST
                return response
        
        except Exception as e:
            response.data = {
                "status": "error",
                "message": str(e) 
            }
            response.status_code = 400
            return response


class UpdateProfile(APIView):   
    @Autherize()
    def get(self, request, **kwargs):  # Endpoint to GET user profile
        try:
            user = kwargs['user']
            profile = user.profile  # Accessing the associated profile directly
            profile_data = {
                "firstname": profile.firstname,
                "lastname": profile.lastname,
                "profile_picture": profile.profile_picture,
                "bio": profile.bio,
                "country": profile.country,
                "native_language": profile.native_language,
                "gender": profile.gender,
                "date_of_birth": profile.date_of_birth,
                "phone_number": profile.phone_number,
                "daily_goal": profile.daily_goal,
                "requirement": profile.requirement
            }
            return JsonResponse(profile_data, status=200)

        except UserProfile.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)
        except KeyError:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    @Autherize()
    def post(self, request, **kwargs):  # Endpoint to update user profile
            user = kwargs['user']

            # firstname = request.data['firstname']
            # lastname = request.data['lastname']
            # profile_picture = request.data.get('profile_picture', None)
            # bio = request.data.get('bio', None)
            # country = request.data.get('country', None)
            # native_language = request.data.get('native_language', None)
            # gender = request.data.get('gender', None)
            # date_of_birth = request.data.get('date_of_birth', None)
            # phone_number = request.data['phone_number']
            # requirement = request.data.get('requirement', UserProfile.Requirement.other)
            # daily_goal = request.data['daily_goal']

            serializer = UpdateProfileSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    profile = user.profile

                    profile.firstname = serializer.validated_data['firstname']    # MOST OF THESE DATA SHOULD BE VALIDATED FROM THE FRONTEND
                    profile.lastname = serializer.validated_data['lastname']
                    profile.profile_picture = serializer.validated_data['profile_picture']
                    profile.bio = serializer.validated_data['bio']
                    profile.country = serializer.validated_data['country']
                    profile.native_language = serializer.validated_data['native_language']
                    profile.gender = serializer.validated_data['gender']
                    profile.date_of_birth = serializer.validated_data['date_of_birth']
                    profile.phone_number = serializer.validated_data['phone_number']
                    profile.requirement = serializer.validated_data['requirement']
                    profile.daily_goal = serializer.validated_data['daily_goal']

                    profile.save()

                    return JsonResponse({
                        "status": "success",
                        "message": "Profile updated successfully",
                    }, status=200)

                except UserProfile.DoesNotExist:
                    return JsonResponse({
                        "status": "error",
                        "message": "Profile not found"
                    }, status=404)
            else:
                return JsonResponse(serializer.errors, status=400)
        

class Login(APIView):
    
    @Autherize()
    def get(self,request,**kwargs):
        
        user = kwargs['user']
        return JsonResponse(
            {
                "id":user.id,
                "username":user.username,
                "email":user.email,
                "login_type":user.login_type
            },
            status=200
        )
        
    def post(self, request):  # ENDPOINT TO LOGIN
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
            
        user = serializer.validated_data['user']
        token = generate_jwt_token(user)
        refresh_token = generate_jwt_token(user, is_refresh=True)
        
        user.is_loggedin = True
        user.save()
        response = Response()
        response.data ={
                    "id":user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "login_type": user.login_type,
                    # "token":token,
                    # "refresh_token":refresh_token
                    }
        response.status_code = 200
        response.set_cookie("jwt",token, httponly=True, secure=True, samesite="Lax")
        response.set_cookie("refresh_token",refresh_token, httponly=True, secure=True, samesite="Lax")
        
        return response


class Logout(APIView):
    @Autherize()
    def post(self,request,**kwargs):
        response = Response()
        user = kwargs['user']
        user.is_loggedin = False
        user.save()
        response.data = {
            "status": "success",
            "message": "Logged out successfully"
        }
        response.status_code = 200
        response.delete_cookie("jwt",samesite="Lax")
        response.delete_cookie("refresh_token",samesite="Lax")
        return response

class EmailVerificationRequest(APIView):
    def post(self,request):
        serializer = EmailVerificationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']
        user = UserAuth.objects.get(email=email)
        if user.email_verified:
            return Response({"status": "error", "message": "Email already verified"}, status=400)
        otp = otp_set_and_gen(email)
        
        msg = f"""
                Hi {user.username},

                You're almost set! Please use the OTP below to verify your email address for Gesturio: \n
                OTP: {otp}
                This code will expire in {settings.OTP_TTL // 60} minutes. If you did not request this, please ignore this message.
                Please also check the spam folder in case the email is not in your inbox. \n\n
                Thanks for choosing Gesturio!
                The Gesturio Team
            """
            
        send_email(
            subject="Your Gesturio Verification Code",
            message=msg,
            to=email
        )
        return JsonResponse({"status": "success", "message": "OTP sent successfully"}, status=200)

class EmailVerificationCheck(APIView):
    def post(self,request):
        serializer = EmailVerificationSerializerOTPCheck(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        check = verify_hash(str(otp),cache.get(f'otp:{email}'))
        if not check:
            return Response({"status": "error", "message": "Invalid OTP"}, status=400)
        cache.delete(f'otp:{email}')
        user = UserAuth.objects.get(email=email)
        user.email_verified = True
        user.save()
        return JsonResponse({"status": "success", "message": "Email verified successfully"}, status=200)
        
