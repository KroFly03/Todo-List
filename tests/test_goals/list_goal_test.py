import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import GoalFactory


@pytest.mark.django_db()
class TestListGoalView:
    url = reverse('goals:list_goal')

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Authentication credentials were not provided.'}

    def test_return_correct_data_keys(self, auth_client, board_participant, goal_category):
        GoalFactory.create_batch(5, category=goal_category)

        response = auth_client.get(self.url)
        print(response.data)
        assert list(response.data[0].keys()) == ['id', 'user', 'created', 'updated', 'title', 'description', 'due_date',
                                                 'status', 'priority', 'category']
        assert list(dict(response.data[0].get('user')).keys()) == ['id', 'username', 'first_name', 'last_name', 'email']

    def test_correct_status_code(self, auth_client):
        GoalFactory.create_batch(5)

        response = auth_client.get('/goals/goal/list')

        assert response.status_code == status.HTTP_200_OK
