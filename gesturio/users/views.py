from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import UserAuth, UserProfile, LoginType
from django.http import JsonResponse
from .utils import generate_jwt_token,Autherize
from .password_utils import verify_hash
from django.core.exceptions import ValidationError


class RegisterAuth(APIView):
    def post(self,request):
        response = Response()
        try:
            username = request.data['username']
            email = request.data['email']
            password = request.data['password']
            if not password:
                response.data = {
                    "status": "error",
                    "message": "Password is required"
                }
                response.status_code = 400
                return response                
        except:
            response.data = {
                "status": "error",
                "message": "Incorrect input"
            }
            response.status_code = 400
            return response

        if UserAuth.objects.filter(username=username).exists() | UserAuth.objects.filter(email=email).exists():
            response.data = {
                "status": "error",
                "message": "Username or email already exists"
            }
            response.status_code = 400
            return response

        user = UserAuth(
            username=username,
            email=email,
            password_hash=password,
            login_type=LoginType.email,
            email_verified=False
        )
        user.save()
        response.data = {
            "status": "success",
            "message": "User registered successfully"
        }
        response.status_code = 201
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
        try:
            user = kwargs['user']

            firstname = request.data['firstname']
            lastname = request.data['lastname']
            profile_picture = request.data.get('profile_picture', None)
            bio = request.data.get('bio', None)
            country = request.data.get('country', None)
            native_language = request.data.get('native_language', None)
            gender = request.data.get('gender', None)
            date_of_birth = request.data.get('date_of_birth', None)
            phone_number = request.data['phone_number']
            requirement = request.data.get('requirement', UserProfile.Requirement.other)
            daily_goal = request.data['daily_goal']

            if requirement not in dict(UserProfile.Requirement.choices):
                return JsonResponse({
                    "status": "error",
                    "message": f"Invalid requirement value. Must be one of: {', '.join(dict(UserProfile.Requirement.choices).keys())}"
                }, status=400)

            try:
                profile = user.profile

                profile.firstname = firstname
                profile.lastname = lastname
                profile.profile_picture = profile_picture
                profile.bio = bio
                profile.country = country
                profile.native_language = native_language
                profile.gender = gender
                profile.date_of_birth = date_of_birth
                profile.phone_number = phone_number
                profile.requirement = requirement
                profile.daily_goal = daily_goal

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

        except KeyError as e:
            return JsonResponse({
                "status": "error",
                "message": f"Missing required field: {str(e)}"
            }, status=400)

        except ValidationError as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "An unexpected error occurred"
            }, status=500)

        

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
        
    def post(self,request):  # ENDPOINT TO LOGIN
        response = Response()
        try:
            username = request.data['username']
            password = request.data['password']

            usernameEntered = UserAuth.objects.filter(username=username).exists()
            emailEntered = UserAuth.objects.filter(email=username).exists()

            if not (usernameEntered | emailEntered):
                response.data = {
                    "status": "error",
                    "message": "Username or email does not exist"
                }
                response.status_code = 404
                return response

        except:
            response.data = {
                "status": "Incorrect input"
                }
            response.status_code = 404
            return response
        
        if usernameEntered:
            user = UserAuth.objects.filter(username=username)
            user = user.first()

        if emailEntered:
            user = UserAuth.objects.filter(email=username)
            user = user.first()
        
        if not (user.login_type == LoginType.email):
            response.data = {
                "status": "error",
                "message": "Please login with username or email , this email is linked with a non-email login type"
            }
            response.status_code = 400
            return response


        if not verify_hash(password,user.password_hash):
            response.data = {
                "status": "Incorrect password"
                }
            response.status_code = 404
            return response
        
        if not hasattr(user, 'profile') or not user.profile.firstname or not user.profile.lastname:
            response.data = {
                "status": "error",
                "message": "Please complete your profile before proceeding"
            }
            response.status_code = 400
            return response
        
        token = generate_jwt_token(user)
        refresh_token = generate_jwt_token(user,is_refresh=True)
           
        user.is_loggedin = True
        user.save()
        
        response.data ={
                    "id":user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "login_type": user.login_type,
                    "token":token,
                    "refresh_token":refresh_token
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
