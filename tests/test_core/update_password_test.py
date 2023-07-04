import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import UserFactory


@pytest.mark.django_db()
class TestVerifyBotView:
    url = reverse('core:update_password')

    def test_auth_required(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Authentication credentials were not provided.'}

    def test_incorrect_old_password(self, auth_client):
        data = {
            'old_password': 'incorrect_old_password',
            'new_password': '1qa2ws3ed'
        }

        response = auth_client.put(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['Incorrect old password.']}

    def test_correct_old_password(self, client):
        password = '1qa2ws3ed4rf5tg'

        user = UserFactory.create(password=password)

        client.force_authenticate(user=user)

        data = {
            'old_password': password,
            'new_password': '1qa2ws3ed'
        }

        response = client.put(self.url, data=data)

        assert response.status_code == status.HTTP_200_OK
