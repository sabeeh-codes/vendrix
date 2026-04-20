from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'password', 'password2']

    # check if both passwords match
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    # create new user with hashed password
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        return user


# login using email instead of username
class EmailLoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email    = data.get('email', '').lower().strip()
        password = data.get('password', '')

        # try to find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'email': 'No account found with this email.'}
            )

        # check password
        if not user.check_password(password):
            raise serializers.ValidationError(
                {'password': 'Incorrect password.'}
            )

        # check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                {'email': 'This account is disabled.'}
            )

        # generate jwt tokens
        refresh = RefreshToken.for_user(user)

        # return tokens + basic user info
        return {
            'access':   str(refresh.access_token),
            'refresh':  str(refresh),
            'username': user.username,
            'email':    user.email,
            'user_id':  user.id,
        }


# serializer for user profile (view/update)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model        = User
        fields       = ['id', 'username', 'email', 'phone', 'address', 'created_at']

        # these fields cannot be changed
        read_only_fields = ['id', 'created_at']