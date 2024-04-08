from rest_framework import serializers

from ib_core.models import UUIDModel


class UUIDModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UUIDModel
        read_only_fields = ['id', 'tag_manager', 'creator', 'create_date_time_stamp', 'deleted']
