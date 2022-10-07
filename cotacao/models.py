from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    abbr = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Rate(models.Model):
    date = models.DateField()
    base = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='base'
    )
    to = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='to')
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=4
    )

    def __str__(self):
        return f'{self.date} - {self.base} - {self.to} - {self.rate}'

    class Meta:
        unique_together = ('date', 'base', 'to')
