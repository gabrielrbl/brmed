from rest_framework.serializers import ModelSerializer
from cotacao.models import Currency, Rate


class CurrencySerializer(ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class RateSerializer(ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'
        depth = 2
