from rest_framework import serializers
from .models import UserAuth, UserProfile, LoginType
import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .password_utils import verify_hash

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

        # Check if username exists as username or email
        username_exists = UserAuth.objects.filter(username=username).exists()
        email_exists = UserAuth.objects.filter(email=username).exists()

        if not (username_exists or email_exists):
            raise serializers.ValidationError({
                "status": "error",
                "message": "Username or email does not exist"
            })

        # Get user based on whether username was email or username
        if username_exists:
            user = UserAuth.objects.get(username=username)
        else:
            user = UserAuth.objects.get(email=username)

        # Check login type
        if user.login_type != LoginType.email:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Please login with username or email, this email is linked with a non-email login type"
            })

        # Verify password
        if not verify_hash(password, user.password):
            raise serializers.ValidationError({
                "status": "error",
                "message": "Incorrect password"
            })

        # Check if profile is complete
        if not hasattr(user, 'profile') or not user.profile.firstname or not user.profile.lastname:
            raise serializers.ValidationError({
                "status": "error",
                "message": "Please complete your profile before proceeding"
            })

        # Add user to validated data for use in view
        data['user'] = user
        return data

    
