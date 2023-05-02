from adrf.views import APIView
from api.models import MailProvider
from api.serializers import ProviderSerializer
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.pagination import PageNumberPagination


class ProvidersListView(APIView):
    """
    Список провайдеров с пагинацией
    """

    serializer_class = ProviderSerializer
    pagination_class = PageNumberPagination

    @extend_schema(
        responses=ProviderSerializer(many=True),
    )
    async def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = settings.PAGINATION_SIZE

        queryset = MailProvider.objects.all()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProviderSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
