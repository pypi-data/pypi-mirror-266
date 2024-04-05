from django.db import models


class Profile(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True)
    created = models.DateTimeField('Создано', auto_now_add=True)
    updated = models.DateTimeField('Изменено', auto_now=True)
    # ФИО
    first_name = models.CharField('Имя', max_length=32)
    last_name = models.CharField('Фамилия', max_length=32)
    middle_name = models.CharField('Отчество', max_length=32)
    birth_date = models.DateField('Дата рождения')
    # Идентификация, верификация
    identified = models.DateTimeField('Идентифицирован', null=True, blank=True)
    verified = models.DateTimeField('Верифицирован', null=True, blank=True)
    # Паспорт
    passport_serial = models.CharField('Серия', max_length=4)
    passport_number = models.CharField('Номер', max_length=6)
    passport_birth_place = models.CharField('Место рождения', max_length=256, blank=True)
    passport_issue_name = models.CharField('Кем выдан', max_length=256, blank=True)
    passport_code = models.CharField('Код паспорта', max_length=16)
    passport_date = models.DateField('Дата выдачи', )
    # Прочие документы
    snils = models.CharField('Снилс', max_length=64, null=True, blank=True)
    # Адрес
    postal_code = models.CharField('Индекс', max_length=16, blank=True)
    state = models.CharField('Регион', max_length=256, blank=True)
    city = models.CharField('Город', max_length=256, blank=True)
    street = models.CharField('Улица', max_length=256, blank=True)
    house = models.CharField('Дом', max_length=8, blank=True)
    apt = models.CharField('Кв', max_length=8, blank=True)
    # Прочее
    income = models.PositiveIntegerField('Доход', blank=True, null=True, help_text='Ежемесячный доход')

    def __str__(self):
        return f'{self.user_id}'

    class Meta:
        managed = False
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        unique_together = (('passport_serial', 'passport_number', ),
                           ('first_name', 'last_name', 'middle_name', 'birth_date'),
                           )
        constraints = (models.UniqueConstraint(fields=('first_name', 'last_name', 'middle_name', 'birth_date'),
                                               name='unique_full_name'),
                       models.UniqueConstraint(fields=('passport_serial', 'passport_number', ),
                                               name='unique_passport'),
                       )
