from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import pandas as pd
from cotacao.utils import VATApi
from cotacao.models import Currency, Rate
from cotacao.serializers import CurrencySerializer, RateSerializer


def home(request):
    currencies = Currency.objects.all()
    context = {
        'currencies': currencies,
        'default_currency': settings.DEFAULT_CURRENCY
    }

    if request.method == 'POST':
        params = request.POST.dict()

        required_fields = ['start', 'finish', 'currency']

        for field in required_fields:
            if field not in params:
                return HttpResponse('Missing field: {}'.format(field))

        try:
            start = pd.to_datetime(params['start'])
            finish = pd.to_datetime(params['finish'])
        except ValueError:
            return HttpResponse('Invalid date format')

        if (start or finish) > pd.to_datetime('today'):
            return HttpResponse('Invalid date')

        try:
            currency = Currency.objects.get(abbr=params['currency'])
        except Currency.DoesNotExist:
            return HttpResponse('Invalid currency')

        date_range = pd.date_range(start=start, end=finish, freq='D')

        api = VATApi('rates')

        data = []

        for date in date_range:
            # CHECK IF DATE IS TODAY TO UPDATE THE RATE FROM API
            if date == pd.to_datetime('today'):
                rate, updated = api.get_or_update_rate(date, currency)
            else:
                rate, created = api.get_or_create_rate(date, currency)

            data.append({'date': date, 'rate': rate.rate})

        context['to'] = currency
        context['data'] = data

        context['selected_start'] = start
        context['selected_finish'] = finish
        context['selected_currency'] = currency

    return render(request, 'home.html', context)


class CurrencyViewSet(ModelViewSet):
    """API endpoint that allows currencies to be viewed or edited."""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class RateViewSet(ModelViewSet):
    """API endpoint that allows rates to be viewed or edited."""
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
