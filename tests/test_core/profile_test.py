import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestVerifyBotView:
    url = reverse('core:profile')

    def test_auth_required(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Authentication credentials were not provided.'}

    def test_return_correct_data_keys(self, auth_client):
        response = auth_client.get(self.url)

        assert list(response.data.keys()) == ['id', 'username', 'first_name', 'last_name', 'email']

    def test_correct_status_code(self, auth_client):
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK