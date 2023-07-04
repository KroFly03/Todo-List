import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import BoardParticipant


@pytest.mark.django_db()
class TestCreateGoalView:
    url = reverse('goals:create_goal')

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Authentication credentials were not provided.'}

    def test_failed_to_create_gaol_if_not_participant(self, auth_client, goal_category, faker):
        data = {'category': goal_category.id, 'title': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'You do not have permission to perform this action.'}

    def test_failed_to_create_goal_if_reader(self, auth_client, board_participant, goal_category, faker):
        board_participant.role = BoardParticipant.Role.reader
        board_participant.save()

        data = {'category': goal_category.id, 'title': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'You do not have permission to perform this action.'}

    @pytest.mark.parametrize('role', [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                             ids=['owner', 'writer'])
    def test_success_to_create_goal_if_owner_or_writer(self, auth_client, board_participant, goal_category, faker,
                                                       role):
        board_participant.role = role
        board_participant.save()

        data = {'category': goal_category.id, 'title': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_return_correct_data_keys(self, auth_client, board_participant, goal_category, faker):
        board_participant.role = BoardParticipant.Role.owner
        board_participant.save()

        data = {'category': goal_category.id, 'title': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert list(response.data.keys()) == (['id', 'created', 'updated', 'title', 'description', 'due_date', 'status',
                                               'priority', 'category'])

    def test_failed_to_create_goal_with_deleted_category(self, auth_client, board_participant, goal_category, faker):
        goal_category.is_deleted = True
        goal_category.save()

        data = {'category': goal_category.id, 'title': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Category is deleted.']}

    def test_failed_to_create_goal_with_not_exist_category(self, auth_client, board_participant, faker):
        data = {'category': 10, 'title': faker.sentence()}

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Invalid pk "10" - object does not exist.']}
