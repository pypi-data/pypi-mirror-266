from ib_core.mixins.authorization import TokenAuthorizationMixin
from rest_framework import generics, status


class DeleteFullBasicAPIView(TokenAuthorizationMixin, generics.DestroyAPIView):
    only_admins = True
    queryset = None

    def perform_destroy(self, instance):
        instance.db_delete()
