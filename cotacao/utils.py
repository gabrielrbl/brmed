from django.conf import settings
import pandas as pd
import requests
from cotacao.models import Currency, Rate


class VATApi:
    def __init__(self) -> None:
        api = settings.VAT_API
        self.default_currency = 'USD'
        self.url = f'{api}/rates/?base={self.default_currency}'

    def get_rates_by_date(self, date: pd.Timestamp) -> dict:
        response = requests.get(
            self.url,
            params={'date': date.strftime('%Y-%m-%d')}
        )
        response.raise_for_status()
        return response.json()['rates']

    def create_rate(self, date: pd.Timestamp, currency: Currency, rate: float) -> Rate:
        rate = Rate.objects.create(
            date=date,
            base=Currency.objects.get(abbr=self.default_currency),
            to=currency,
            rate=rate,
        )
        return rate

    def get_or_create_rate(self, date: pd.Timestamp, currency: Currency) -> Rate:
        try:
            rate = Rate.objects.get(
                date=date,
                base=Currency.objects.get(abbr=self.default_currency),
                to=currency,
            )
            created = False
        except Rate.DoesNotExist:
            search = self.get_rates_by_date(date)

            if not currency.abbr in search:
                raise ValueError('Currency not found')

            rate = self.create_rate(date, currency, search[currency.abbr])
            created = True
        return rate, created

    def get_or_update_rate(self, date: pd.Timestamp, currency: Currency) -> Rate:
        try:
            rate = Rate.objects.get(
                date=date,
                base=Currency.objects.get(abbr=self.default_currency),
                to=currency,
            )
            rate.rate = rate
            rate.save()
            updated = True
        except Rate.DoesNotExist:
            search = self.get_rates_by_date(date)

            if not currency.abbr in search:
                raise ValueError('Currency not found')

            rate = self.create_rate(date, currency, search[currency.abbr])
            updated = False
        return rate, updated
