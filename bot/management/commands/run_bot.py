from datetime import timedelta
from typing import Callable, Any

from django.core.management import BaseCommand
from django.utils import timezone
from pydantic import BaseModel

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory, Board


class FSMData(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.clients: dict[int, FSMData] = {}

    def handle(self, *args, **options) -> None:
        offset = 0

        self.stdout.write(self.style.SUCCESS('Bot started'))
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, message: Message) -> None:
        tg_user, _ = TgUser.objects.get_or_create(chat_id=message.chat.id)

        if tg_user.user:
            self.handle_authorized_user(tg_user, message)
        else:
            self.tg_client.send_message(tg_user.chat_id,
                                        f'Приветствую!\n'
                                        f'Чтобы использовать данного бота, '
                                        f'необходимо подтверидить аккаунт на сайте с помощью кода.')

            tg_user.update_verification_code()
            self.tg_client.send_message(tg_user.chat_id, f'Ваш код подтверждения: {tg_user.verification_code}')

    @staticmethod
    def _board_display(boards: list[Board]) -> str:
        return 'Ваши доски:\n' + '\n\n'.join([
            f'Доска №{board.id}\nНазвание: {board.title}\nСоздано: '
            f'{board.created.date()}\nОбновлено: {board.updated.date()}'
            for board in boards]) + '\n\nВыберите доску'

    @staticmethod
    def _goal_display(goals: list[Goal]) -> str:
        return 'Ваши цели:\n' + '\n\n'.join([
            f'Цель №{goal.id}\nНазвание: {goal.title}\nСоздано: {goal.created.date()}\n'
            f'Обновлено: {goal.updated.date()}\n' \
            f'Описание: {goal.description if goal.description else "Отсутствует"}\nДедлайн: {goal.due_date}\n' \
            f'Приоритет: {Goal.Priority(goal.priority).name}\nСтатус: {Goal.Status(goal.status).name}\n'
            f'Категория: {goal.category.title}'
            for goal in goals])

    @staticmethod
    def _category_display(categories: list[GoalCategory]) -> str:
        return 'Ваши категории:\n' + '\n\n'.join([
            f'Категория №{category.id}\nНазвание: {category.title}\nСоздано: '
            f'{category.created.date()}\nОбновлено: {category.updated.date()}'
            for category in categories]) + '\n\nВыберите категорию'

    def handle_authorized_user(self, tg_user: TgUser, message: Message) -> None:
        if message.text.startswith('/'):
            match message.text:
                case '/help':
                    self.handle_help_command(tg_user, message)
                case '/boards':
                    self.handle_boards_command(tg_user, message)
                case '/create':
                    self.handle_boards_command(tg_user, message, create=True)
                case '/cancel':
                    self.handle_cancel_command(tg_user, message)
                case _:
                    self.tg_client.send_message(tg_user.chat_id, 'Команда не найдена')
        elif tg_user.chat_id in self.clients:
            client = self.clients[tg_user.chat_id]
            client.next_handler(tg_user=tg_user, message=message, **client.data)
        else:
            self.tg_client.send_message(tg_user.chat_id, f'Прошу прощения, я не понимаю, что <{message.text}> значит\n'
                                                         f'Введите /help, чтобы посмотреть доступные команды')

    def handle_help_command(self, tg_user: TgUser, message: Message) -> None:
        text = 'Вам доступны следующие команды:\n' + '\n'.join(['/help', '/boards', '/create', '/cancel'])
        self.tg_client.send_message(tg_user.chat_id, text)

    def handle_boards_command(self, tg_user: TgUser, message: Message, create: bool = False) -> None:
        boards = Board.objects.filter(participants__user=tg_user.user).exclude(is_deleted=True)

        if boards:
            text = self._board_display(boards)
            self.clients[tg_user.chat_id] = FSMData(next_handler=self._get_boards, data={'create': create})
        else:
            text = 'У Вас нет досок'

        self.tg_client.send_message(tg_user.chat_id, text)

    def handle_cancel_command(self, tg_user: TgUser, message: Message) -> None:
        self.clients.pop(tg_user.chat_id, None)
        self.tg_client.send_message(tg_user.chat_id, 'Действие отменено')

    def _get_boards(self, tg_user: TgUser, message: Message, **kwargs) -> None:
        try:
            board = Board.objects.get(pk=message.text, participants__user=tg_user.user)
        except Board.DoesNotExist:
            self.tg_client.send_message(tg_user.chat_id, 'Доски не существует\nДля отмены действия введите команду '
                                                         '/cancel')
            return
        except ValueError:
            self.tg_client.send_message(tg_user.chat_id, 'Вводимое значение должно являться числом\n'
                                                         'Для отмены действия введите команду '
                                                         '/cancel')
            return
        else:
            if kwargs['create']:
                self._show_categories(tg_user, message, board)
            else:
                self._show_goals(tg_user, message, board)

    def _show_categories(self, tg_user: TgUser, message: Message, board):
        categories = GoalCategory.objects.filter(board__participants__user=tg_user.user, board=board) \
            .exclude(is_deleted=True)

        if categories:
            text = self._category_display(categories)
        else:
            self.tg_client.send_message(tg_user.chat_id, 'У Вас нет категорий на данной доске')
            self.clients.pop(tg_user.chat_id, None)
            return

        self.tg_client.send_message(tg_user.chat_id, text)
        self.clients[tg_user.chat_id] = FSMData(next_handler=self._get_category,
                                                data={'board': board})

    def _show_goals(self, tg_user: TgUser, message: Message, board):
        goals = Goal.objects.filter(category__board__participants__user=tg_user.user,
                                    category__is_deleted=False, category__board=board).exclude(
            status=Goal.Status.archived)

        if goals:
            text = self._goal_display(goals)
        else:
            text = 'У Вас нет целей на данной доске'

        self.tg_client.send_message(tg_user.chat_id, text)

    def _get_category(self, tg_user: TgUser, message: Message, **kwargs) -> None:
        try:
            category = GoalCategory.objects.get(pk=message.text, **kwargs)
        except GoalCategory.DoesNotExist:
            self.tg_client.send_message(tg_user.chat_id, 'Категории не существует')
            return

        else:
            self.clients[tg_user.chat_id] = FSMData(next_handler=self._create_goal, data={'category': category})
            self.tg_client.send_message(tg_user.chat_id, 'Задайте название цели')

    def _create_goal(self, tg_user: TgUser, message: Message, **kwargs) -> None:
        category = kwargs['category']
        Goal.objects.create(category=category, user=tg_user.user, title=message.text,
                            due_date=timezone.now() + timedelta(days=7))
        self.tg_client.send_message(tg_user.chat_id, 'Новая цель создана')
        self.clients.pop(tg_user.chat_id, None)
