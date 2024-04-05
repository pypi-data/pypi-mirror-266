from django.db import models


class BlackList(models.Model):
    EMPTY = 'EMPTY'
    SCORING = 'SCORING'
    FRAUD = 'FRAUD'
    NOT_INTEREST = 'NOT_INTEREST'
    LEGAL = 'LEGAL'
    SPAM = 'SPAM'

    CAUSE_CHOICES = (
        (EMPTY, 'Не указана'),
        (SCORING, 'Низкий скор'),
        (FRAUD, 'Мошенник'),
        (NOT_INTEREST, 'Просил заблокировать'),
        (LEGAL, 'Юр. ограничения'),
        (SPAM, 'Бот/Спам'),

    )
    created = models.DateTimeField('Добавлен', auto_now_add=True)
    user_id = models.CharField(blank=True, max_length=128)
    cause = models.CharField('Причина', max_length=16, choices=CAUSE_CHOICES, default=EMPTY, null=True)
    passport_serial = models.CharField('Серия паспорта', max_length=4, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=6, blank=True)
    comment = models.CharField('Комментарий', max_length=128, blank=True)

    def __str__(self):
        return f'{self.user_id}'

    class Meta:
        managed = False
        verbose_name = 'Черный список'
        verbose_name_plural = 'Черный список'
