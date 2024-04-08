from rest_framework import generics
from rest_framework.response import Response

from ib_core.mixins.authorization import TokenAuthorizationMixin
from ib_core.serializers.common import UUIDModelSerializer


class GetObjectByKeyBaseAPIView(TokenAuthorizationMixin, generics.RetrieveAPIView):
    model = None
    serializer_class = None
    lookup_field = 'pk'
    to_dict_kwargs = {}

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.to_dict_kwargs.get("auth"):
            self.to_dict_kwargs["auth"] = self.auth
        return Response(instance.to_dict(**self.to_dict_kwargs))


class BaseListAPIView(TokenAuthorizationMixin, generics.ListAPIView):
    serializer_class = UUIDModelSerializer
    queryset = None
    pagination_class = None

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        data = [obj.to_dict() for obj in list(page)]
        return self.get_paginated_response(data)
