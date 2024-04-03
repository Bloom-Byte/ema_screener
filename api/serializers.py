from rest_framework import serializers



class UserIDSerializer(serializers.Serializer):
    """Serializer for user id"""
    user_id = serializers.UUIDField(required=True, write_only=True, allow_null=False)
