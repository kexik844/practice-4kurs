import django_filters
from .models import Service


class ServiceFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )

    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )

    class Meta:
        model = Service
        fields = ['category', 'is_available']