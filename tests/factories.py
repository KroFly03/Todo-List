import factory.django
from django.utils import timezone

from bot.models import TgUser
from core.models import User
from pytest_factoryboy import register

from goals.models import Board, BoardParticipant, GoalCategory, Goal, GoalComment


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return User.objects.create_user(*args, **kwargs)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, owner=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(factory.django.DjangoModelFactory):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    role = 1

    class Meta:
        model = BoardParticipant


@register
class GoalCategoryFactory(DatesFactoryMixin):
    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory


@register
class GoalFactory(DatesFactoryMixin):
    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)

    class Meta:
        model = Goal


@register
class GoalCommentFactory(DatesFactoryMixin):
    text = factory.Faker('sentence')
    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)

    class Meta:
        model = GoalComment


@register
class TgUserFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    chat_id = factory.Faker('random_int', min=1, max=100)

    class Meta:
        model = TgUser
