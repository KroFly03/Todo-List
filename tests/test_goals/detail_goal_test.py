import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import GoalFactory


@pytest.mark.django_db()
class TestDetailGoalView:
    url = reverse('goals:detail_goal', args=[1])

    def test_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Authentication credentials were not provided.'}

    def test_return_correct_data_keys(self, auth_client, board_participant, goal_category):
        goal = GoalFactory.create(category=goal_category)

        self.url = reverse('goals:detail_goal', args=[goal.id])

        response = auth_client.get(self.url)

        assert list(response.data.keys()) == ['id', 'user', 'created', 'updated', 'title', 'description', 'due_date',
                                              'status', 'priority', 'category']
        assert list(dict(response.data.get('user')).keys()) == ['id', 'username', 'first_name', 'last_name', 'email']

    def test_correct_status_code(self, auth_client, board_participant, goal_category):
        goal = GoalFactory.create(category=goal_category)

        self.url = reverse('goals:detail_goal', args=[goal.id])

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

        self.url = reverse('goals:detail_goal', args=[50])

        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
