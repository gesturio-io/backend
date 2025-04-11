from rest_framework import serializers
from .models import UserAuth, UserProfile, LoginType, UserLoginLog
import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .password_utils import verify_hash
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, date

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuth
        fields = ['username', 'email', 'password']

    def validate(self, data):   
        
        if not data.get('password'):
            raise serializers.ValidationError({
                "status": "error",
                "message": "Password is required"
            })
        if len(data.get('password')) < 5:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Password must be at least 5 characters long"
            })
        if data.get('username') in ['admin', 'root', 'superuser', 'super', 'superuser']:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Username is not allowed"
            })
        if UserAuth.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError({
                "status": "error",
                "message": "Username already exists"
            })
        if UserAuth.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({
                "status": "error",
                "message": "Email already exists"
            })
            
        return data

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'firstname', 'lastname', 'profile_picture', 
            'bio', 'country', 'native_language', 'gender', 
            'date_of_birth', 'phone_number', 'requirement', 'daily_goal'
        ]

    def validate(self, data):
        
        missing_fields = []
        
        for field in self.Meta.fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            raise serializers.ValidationError({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            })
        
        if (data.get('firstname') in ['admin', 'root', 'superuser', 'super', 'superuser']) or (data.get('lastname') in ['admin', 'root', 'superuser', 'super', 'superuser']):
            raise serializers.ValidationError({
                "status": "error",
                "message": "Name is not allowed"
            })
        
        
        if data.get('profile_picture'):
            validator = URLValidator()
            validator(data.get('profile_picture'))
            
        if data.get('phone_number'):
            cleaned_phone = re.sub(r'\D', '', data.get('phone_number'))
            if len(cleaned_phone) > 10:
                raise ValidationError({'phone_number': 'Phone number must be 10 digits'})
            if not all(c.isdigit() for c in data.get('phone_number')):
                raise ValidationError({'phone_number': 'Phone number can only contain digits'})
            data['phone_number'] = cleaned_phone
        
        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        username_exists = UserAuth.objects.filter(username=username).exists()
        email_exists = UserAuth.objects.filter(email=username).exists()

        if not (username_exists or email_exists):
            raise serializers.ValidationError({
                "status": "error",
                "message": "Username or email does not exist"
            })

        if username_exists:
            user = UserAuth.objects.get(username=username)
        else:
            user = UserAuth.objects.get(email=username)

        if user.login_type != LoginType.email:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Please login with username or email, this email is linked with a non-email login type"
            })

        if not verify_hash(password, user.password):
            raise serializers.ValidationError({
                "status": "error",
                "message": "Incorrect password"
            })
        if not user.email_verified:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Please verify your email before proceeding"
            })
        data['user'] = user
        return data

class EmailVerificationRequestSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)

    def validate(self, data):
        id = data.get('id')
        if not (UserAuth.objects.filter(email=id).exists() or UserAuth.objects.filter(username=id).exists()):
            raise serializers.ValidationError({
                "status": "error",
                "message": "User with this email or username does not exist"
            })
        if UserAuth.objects.filter(email=id).exists():
            user = UserAuth.objects.get(email=id)
        elif UserAuth.objects.filter(username=id).exists():
            user = UserAuth.objects.get(username=id)
        data['email'] = user.email
        return data
    
class EmailVerificationSerializerOTPCheck(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        if not UserAuth.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "status": "error",
                "message": "User with this email does not exist"
            })
        if not cache.get(f'otp:{email}'):
            raise serializers.ValidationError({
                "status": "error",
                "message": "OTP has expired"
            })
        return data

class UserLoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginLog
        fields = ['user_id', 'ip_address', 'page_url', 'visit_date']
        read_only_fields = ['created_at',]
    
    def validate(self, data):
        
        # Check if visit_date is provided and in correct format
        visit_date = data.get('visit_date')
        if visit_date:
            try:
                if isinstance(visit_date, str):
                    parsed_date = datetime.strptime(visit_date, '%Y-%m-%d').date()
                    data['visit_date'] = parsed_date
                elif not isinstance(visit_date, (datetime, date)):
                    raise ValueError("Invalid date format")
            except (ValueError, TypeError):
                data['visit_date'] = timezone.now().date()
        else:
            
            data['visit_date'] = timezone.now().date()
        
        if not data.get('user_id'):
            raise serializers.ValidationError({
                "status": "error",
                "message": "User ID is required"
            })
        
        if data.get('page_url'):
            try:
                validator = URLValidator()
                validator(data.get('page_url'))
            except ValidationError:
                raise serializers.ValidationError({
                    "status": "error",
                    "message": "Invalid page URL format"
                })
        
        return data

