from django.db import models


class BankCard(models.Model):
    created = models.DateTimeField('Создана', auto_now_add=True)
    updated = models.DateTimeField('Изменена', auto_now=True)
    user_id = models.PositiveIntegerField()
    is_active = models.BooleanField('Активна', default=True)
    bin = models.CharField('Бин', max_length=6)
    number = models.CharField('Номер', max_length=4)
    expiry_month = models.PositiveSmallIntegerField('Месяц')
    expiry_year = models.PositiveSmallIntegerField('Год')
    token = models.CharField('Токен', max_length=1024, unique=True)

    def __str__(self):
        return f'{self.bin}****{self.number}'

    class Meta:
        managed = False
        verbose_name_plural = 'Банковские карты'
        verbose_name = 'Банковская карта'
        unique_together = ('bin', 'number', 'expiry_month', 'expiry_year')
        constraints = (
            models.UniqueConstraint(fields=['bin', 'number', 'expiry_month', 'expiry_year'], name='unique_bank_card'),
        )
