import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import UserFactory


@pytest.mark.django_db()
class TestSignUpView:
    url = reverse('core:login')

    def test_correct_authorization(self, client):
        password = '1qa2ws3ed4rf5tg'

        user = UserFactory(password=password)

        data = {
            'username': user.username,
            'password': password,
        }

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_200_OK
