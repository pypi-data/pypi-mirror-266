from django.utils import timezone
from rest_framework import serializers

from ib_core.models import ActivityPeriod
from ib_core.serializers.tag_binder_serializers import TextTagBinderSerializer, FileTagBinderSerializer


class InstanceSerializer(serializers.Serializer): # noqa
    type = serializers.CharField()
    properties = TextTagBinderSerializer(many=True)
    files = FileTagBinderSerializer(many=True)


class ActivityPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPeriod
        fields = ["start_time", "end_time"]

    def validate(self, data):

        if "start_time" not in data.keys():
            data["start_time"] = timezone.now()

        if data['start_time'] > data['end_time']:
            raise serializers.ValidationError({"stop_date": "finish must occur after start"})
        return data
