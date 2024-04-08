from rest_framework.pagination import PageNumberPagination


class SmallPagesPagination(PageNumberPagination):
    page_size = 20


class MediumPagesPagination(PageNumberPagination):
    page_size = 50


class BigPagesPagination(PageNumberPagination):
    page_size = 100


class BigPagesPlusPagination(PageNumberPagination):
    page_size = 1000
