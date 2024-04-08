from ib_core.mixins.authorization import TokenAuthorizationMixin
from rest_framework import generics, status
from rest_framework.response import Response


class CreateBaseAPIView(TokenAuthorizationMixin, generics.CreateAPIView):
    serializer_class = None
    model = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.model(
            **serializer.validated_data,
            creator=self.user_id
        )
        instance.save()
        return Response(data=instance.to_dict(), status=status.HTTP_201_CREATED)
