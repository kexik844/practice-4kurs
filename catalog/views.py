from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ServiceFilter
from .models import Category, Service, ServiceRequest
from .serializers import (
    CategorySerializer,
    ServiceSerializer,
    ServiceRequestSerializer,
    ServiceRequestCreateSerializer
)
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        category = self.get_object()

        queryset = category.services.select_related(
            'category'
        ).order_by('id')

        if not request.user.is_staff:
            queryset = queryset.filter(is_available=True)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = ServiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.select_related('category')
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = ServiceFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']
    ordering = ['id']

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset.all()

        return self.queryset.filter(is_available=True)


class ServiceRequestViewSet(ModelViewSet):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]

        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceRequestCreateSerializer

        return ServiceRequestSerializer

    def perform_create(self, serializer):
        serializer.save(status='new')