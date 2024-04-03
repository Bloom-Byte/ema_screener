from rest_framework import serializers



class UserIDSerializer(serializers.Serializer):
    """Serializer for user id"""
    user_id = serializers.UUIDField(required=True, allow_null=False)



class PasswordResetTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, allow_null=False)



class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request data"""
    user_id = serializers.UUIDField(required=True, allow_null=False)
    token_name = serializers.CharField(required=False, default="token")    



class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset data"""
    new_password = serializers.CharField(required=True, allow_null=False)
    token = serializers.CharField(required=True, allow_null=False)
