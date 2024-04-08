from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ib_core.mixins.authorization import TokenAuthorizationMixin
from ib_core.models import TagManager
from ib_core.serializers.tag_binder_serializers import TextTagBinderSerializer
from ib_core.utils.uuid_manager import is_valid_uuid


class AddTextTagToObjectBaseAPIView(TokenAuthorizationMixin, APIView):
    """
    Base API View for adding text tag to any model inherited from UUIDModel.

        - In URLConf for API method inherited from AddTextTagToObjectBaseAPIView must be correctly specified kwargs (according to lookup_field)
        - CAUTION: Don't use TokenAuthorizationMixin if method inherited from AddTextTagToObjectBaseAPIView, it already included.

    Attributes
    ----------
        model: UUIDModel
            the model for which the tag is being added (required).
        lookup_field: str
            a field for searching for a specific entity (default: pk).
    ----------
    """
    model = None
    lookup_field = 'pk'
    use_uuid_validation = True

    def post(self, request, *args, **kwargs):
        serializer = TextTagBinderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance_id = self.kwargs.get(self.lookup_field)
        if self.use_uuid_validation and not is_valid_uuid(instance_id):
            return Response(
                {
                    "detail": f"The value '{instance_id}' is not a valid UUID."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        instance = self.model.filter(pk=instance_id).first()
        if not instance:
            return Response(
                {
                    "detail": f"{self.model.__name__} with id '{instance_id}' not found."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        success = instance.tag_manager.add_tag(
            **serializer.validated_data,
            creator=self.user.get_id(),
            auth=self.auth
        )
        return Response(
            dict(
                success=success
            ),
            status=status.HTTP_200_OK
        )


class GetObjectsByTagBaseAPIView(TokenAuthorizationMixin, APIView):
    model = None

    def post(self, request, *args, **kwargs):
        serializer = TextTagBinderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        managers_id = [
            str(manager.pk) for manager in TagManager.filter_by_property_value(
                key=serializer.validated_data.get("key"),
                value=serializer.validated_data.get("content"),
                auth=self.auth
            )
        ]
        print(managers_id)
        instances = list(self.model.objects.filter(tag_manager__in=managers_id))
        print(instances)
        return Response(
            data=[instance.to_dict() for instance in instances]
        )
