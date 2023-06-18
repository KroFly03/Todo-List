from django.db import models

from core.models import User
from todolist.models import BaseModel


class GoalCategory(BaseModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    title = models.CharField(verbose_name='Название', max_length=255)
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)

    def __str__(self):
        return self.title


class Goal(BaseModel):
    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание', blank=True)
    category = models.ForeignKey(verbose_name='Категория', to=GoalCategory, on_delete=models.PROTECT)
    due_date = models.DateField(verbose_name='Дедлайн', null=True, blank=True)
    user = models.ForeignKey(verbose_name='Пользователь', to=User, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        verbose_name='Статус', choices=Status.choices, default=Status.to_do
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name='Приоритет', choices=Priority.choices, default=Priority.medium
    )

    def __str__(self):
        return self.title


class GoalComment(BaseModel):
    user = models.ForeignKey(verbose_name='Пользователь', to=User, on_delete=models.PROTECT)
    goal = models.ForeignKey(verbose_name='Задача', to=Goal, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')

    def __str__(self):
        return self.text
