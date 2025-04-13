from django.conf import settings
from django.shortcuts import redirect
from django.db import models
from .serializers import RegisterSerializer, UpdateProfileSerializer, LoginSerializer, EmailVerificationRequestSerializer, EmailVerificationSerializerOTPCheck, UserLoginLogSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .models import UserAuth, UserProfile, LoginType, UserLoginLog
from django.http import JsonResponse
from .utils import generate_jwt_token,Autherize,otp_set_and_gen,send_email
from .password_utils import verify_hash,generate_hash
from django.core.exceptions import ValidationError
from django.core.cache import cache
import requests
from django.utils import timezone
import json
import re
from gesturio.utility import get_client_ip

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
    def post(self, request):
        response = Response()
        try:
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save(
                    login_type=LoginType.email,
                    email_verified=False
                )
                isProfileComplete = False
                if hasattr(user, 'profile'):
                    profile = user.profile
                    isProfileComplete = bool(profile.firstname and profile.lastname)
                
                response.data = {
                    "id": user.user_id,  # Assuming you have user_id field
                    "email": user.email,
                    "username": user.username,
                    "login_type": user.login_type,
                    "isProfileComplete": isProfileComplete,
                    "status": "success",
                    "message": "User registered successfully"
                }
                
                response.status_code = 201  # CREATED
                
                # Send verification email
                try:
                    req = requests.post(
                        url="http://127.0.0.1:8000/accounts/request-verifyemail/",
                        data={
                            "email": request.data['email']
                        }
                    )
                except requests.RequestException as e:
                    response.data.update({
                        "warning": "Email verification service temporarily unavailable"
                    })
                
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
            response.status_code = 500  # INTERNAL SERVER ERROR
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
                "email": user.email,    
                "joined_at": user.created_at,
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
                    profile.native_language = serializer.validated_data.get('native_language') or profile.native_language
                    profile.gender = serializer.validated_data['gender']
                    profile.date_of_birth = serializer.validated_data.get('date_of_birth') or profile.date_of_birth
                    profile.phone_number = serializer.validated_data.get('phone_number') or profile.phone_number
                    profile.daily_goal = serializer.validated_data.get('daily_goal') or profile.daily_goal

                    profile.save()

                    return JsonResponse({
                        "status": "success",
                        "message": "Profile updated successfully",
                    }, status=200)

                except UserProfile.DoesNotExist:
                    newprofile = UserProfile(
                        user = user,
                        firstname = serializer.validated_data['firstname'],
                        lastname = serializer.validated_data['lastname'],
                        profile_picture = serializer.validated_data['profile_picture'],
                        bio = serializer.validated_data['bio'],
                        country = serializer.validated_data['country'],
                        native_language = serializer.validated_data['native_language'],
                        gender = serializer.validated_data['gender'],
                        date_of_birth = serializer.validated_data['date_of_birth'],
                        phone_number = serializer.validated_data['phone_number'],
                        requirement = serializer.validated_data['requirement'],
                        daily_goal = serializer.validated_data['daily_goal']
                    )
                    newprofile.save()
                    response = Response()
                    response.set_cookie("isProfileComplete", True, httponly=False, secure=True, samesite="Lax")
                    response.data = {
                        "status": "success",
                        "message": "Profile updated successfully",
                    }
                    response.status_code = 201
                    return response
            else:
                print(serializer.errors)
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
        if not hasattr(user, 'profile') or not user.profile.firstname or not user.profile.lastname:
            isProfileComplete = False
        else:
            isProfileComplete = True
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
        response.set_cookie("isProfileComplete", isProfileComplete, httponly=False, secure=True, samesite="Lax")
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
        try:
            otp = otp_set_and_gen(email)
        except Exception as e:
            return Response({"status": "error", "message": "Daily OTP limit exceeded"}, status=400)
        
        msg = f"""
        Hi {user.username},

        Thanks for signing up with Gesturio!

        Your one-time password (OTP) for verifying your email is:

        {otp}

        This code will expire in {settings.OTP_TTL // 60} minutes.

        If you did not request this, please ignore this message.

        Best regards,  
        Team Gesturio  
        https://gesturio.com
        """

        try:
            send_email(
                subject="[noreply@gesturio.com] Your Gesturio Verification Code",
                message=msg,
                to=email
            )
        except Exception as e:
            return JsonResponse({"status": "error in sending email", "message": str(e)}, status=500)
        
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
        

class TrackPageVisit(APIView):
    @Autherize()
    def post(self, request, **kwargs):
        user = kwargs['user']
        response = Response()
        
        # try:
            # Get client IP address
        ip_address = get_client_ip(request)
            
        data = {
                'user_id': user.user_id,
                'ip_address': ip_address,
                'page_url': request.data.get('page_url'),
                'visit_date': request.data.get('visit_date')
        }
            
        serializer = UserLoginLogSerializer(data=data)
            
        if serializer.is_valid():
            serializer.save()    
            response.status_code = 200
                
            return response
            
        else:
                response.data = serializer.errors
                response.status_code = 400
                return response
                
        # except Exception as e:
        #     response.data = {
        #         "status": "error",
        #         "message": str(e)
        #     }
        #     response.status_code = 500
        #     return response
    
    @Autherize()
    def get(self, request, **kwargs):
        user = kwargs.get('user')
        
        try:
            view_type = request.query_params.get('view', 'week')  
            
            if view_type == 'week':
                today = timezone.now().date()
                start_of_week = today - timezone.timedelta(days=today.weekday())
                
                week_dates = [(start_of_week + timezone.timedelta(days=i)) for i in range(7)]
                
                weekly_visits = UserLoginLog.objects.filter(
                    user_id=user,
                    visit_date__gte=start_of_week,
                    visit_date__lte=start_of_week + timezone.timedelta(days=6)
                ).values('visit_date').distinct()
                
                weekly_activity = []
                for date in week_dates:
                    day_data = {
                        'date': date.strftime('%Y-%m-%d'),
                        'day': date.strftime('%a'),
                        'has_activity': any(visit['visit_date'] == date for visit in weekly_visits),
                        'is_today': date == today,
                        'is_future': date > today
                    }
                    weekly_activity.append(day_data)


                streak = 0
                current_date = today
                while True:
                    if UserLoginLog.objects.filter(user_id=user, visit_date=current_date).exists():
                        streak += 1
                        current_date -= timezone.timedelta(days=1)
                    else:
                        break
                
                response_data = {
                    "status": "success",
                    "data": {
                        "weekly_activity": weekly_activity,
                        "current_streak": streak,
                        "daily_goal": user.profile.daily_goal if hasattr(user, 'profile') else 10
                    }
                }
                
            else:  
                end_date = timezone.now().date()
                start_date = end_date - timezone.timedelta(days=29)  # 30 days including today
                
                detailed_visits = UserLoginLog.objects.filter(
                    user_id=user,
                    visit_date__gte=start_date,
                    visit_date__lte=end_date
                ).values('visit_date').annotate(
                    count=models.Count('id')
                ).order_by('-visit_date')
                
                visit_counts = {item['visit_date']: item['count'] for item in detailed_visits}
                
                detailed_data = []
                for i in range(29, -1, -1):  
                    current_date = end_date - timezone.timedelta(days=i)
                    formatted_date = current_date.strftime('%Y-%m-%d')
                    detailed_data.append({
                        'date': formatted_date,
                        'value': visit_counts.get(current_date, 0)  
                    })
                
                response_data = {
                    "status": "success",
                    "data": detailed_data
                }
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)
        
