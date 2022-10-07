from typing import Literal
from django.conf import settings
import pandas as pd
import requests
from cotacao.models import Currency, Rate


class VATApi:
    def __init__(self, endpoint: Literal['rates', 'currencies'] = 'rates') -> None:
        api = settings.VAT_API
        self.default_currency = settings.DEFAULT_CURRENCY
        self.endpoint = endpoint
        url = f'{api}/{endpoint}'

        if endpoint == 'rates':
            url += f'/?base={self.default_currency}'

            if not self.check_currency_in_database(self.default_currency):
                raise ValueError('Default currency not found in database')

        self.url = url

    def check_currency_in_database(self, currency: str) -> bool:
        try:
            Currency.objects.get(abbr=currency)
            return True
        except Currency.DoesNotExist:
            return False

    def get_curriences(self, currencies: list[str]) -> dict[str, dict[str, str]]:
        if self.endpoint != 'currencies':
            raise ValueError('Endpoint must be "currencies"')

        response = requests.get(self.url)
        response.raise_for_status()
        return response.json()


    def get_rates_by_date(self, date: pd.Timestamp) -> dict[str, float]:
        if self.endpoint != 'rates':
            raise ValueError('Endpoint must be "rates"')

        response = requests.get(
            self.url,
            params={'date': date.strftime('%Y-%m-%d')}
        )
        response.raise_for_status()
        return response.json()['rates']

    def create_rate(self, date: pd.Timestamp, currency: Currency, rate: float) -> Rate:
        if self.endpoint != 'rates':
            raise ValueError('Endpoint must be "rates"')

        rate = Rate.objects.create(
            date=date,
            base=Currency.objects.get(abbr=self.default_currency),
            to=currency,
            rate=rate,
        )
        return rate

    def get_or_create_rate(self, date: pd.Timestamp, currency: Currency) -> tuple[Rate, bool]:
        if self.endpoint != 'rates':
            raise ValueError('Endpoint must be "rates"')

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

    def get_or_update_rate(self, date: pd.Timestamp, currency: Currency) -> tuple[Rate, bool]:
        if self.endpoint != 'rates':
            raise ValueError('Endpoint must be "rates"')

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
