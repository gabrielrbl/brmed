import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from cotacao.models import Currency


class Command(BaseCommand):
    help = 'Insert currencies in database'

    def handle(self, *args, **options):
        api = settings.VAT_API

        currencies = ['EUR', 'USD', 'JPY', 'BRL']

        if Currency.objects.count() == 0:
            requisicao = requests.get(f'{api}/currencies')
            moedas = requisicao.json()

            for moeda, dados in moedas.items():
                # ONLY SAVE CURRENCIES IN THE LIST
                if moeda in currencies:
                    Currency.objects.create(
                        name=dados['name'],
                        symbol=dados['symbol'],
                        abbr=moeda
                    )

            self.stdout.write(
                self.style.SUCCESS('Successfully inserted currencies')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Currencies already inserted')
            )
