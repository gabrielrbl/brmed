from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from cotacao.utils import VATApi
from cotacao.models import Currency


def home(request):
    currencies = Currency.objects.all()
    context = {'currencies': currencies}

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

    return render(request, 'home.html', context)
