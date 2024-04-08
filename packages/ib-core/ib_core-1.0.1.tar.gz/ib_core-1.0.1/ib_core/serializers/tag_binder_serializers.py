from rest_framework import serializers


class TextTagBinderSerializer(serializers.Serializer): # noqa
    key = serializers.CharField()
    content = serializers.CharField()
    allow_many = serializers.BooleanField(default=False)


class FileTagBinderSerializer(serializers.Serializer): # noqa
    key = serializers.CharField()
    file = serializers.FileField()
    allow_many = serializers.BooleanField(default=False)
