import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from cotacao.models import Currency
from cotacao.utils import VATApi


class Command(BaseCommand):
    help = 'Insert currencies in database'

    def handle(self, *args, **options):
        self.stdout.write('Checking currencies in database...')
        self.stdout.write('----------------------------------')
        
        count = Currency.objects.count()
        
        self.stdout.write(f'Found {count} currencies in database.')

        api = settings.VAT_API
        
        currencies = ['EUR', 'USD', 'JPY', 'BRL']

        if count == 0:
            self.stdout.write('Inserting currencies in database...')

            api = VATApi('currencies')
            
            moedas = api.get_curriences(currencies)

            for moeda, dados in moedas.items():
                if moeda in currencies:
                    Currency.objects.create(name=dados['name'], symbol=dados['symbol'], abbr=moeda)

            self.stdout.write(
                self.style.SUCCESS('Successfully inserted currencies.')
            )
        self.stdout.write('----------------------------------')
