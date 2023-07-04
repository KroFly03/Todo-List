import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestSignUpView:
    url = reverse('core:signup')

    def test_correct_authorization(self, client):
        data = {
            'username': 'test',
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@mail.ru',
            'password': '1qa2ws3ed4rf5tg',
            'password_repeat': '1qa2ws3ed4rf5tg',
        }

        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_not_equal_password(self, client):
        data = {
            'username': 'test',
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@mail.ru',
            'password': '1qa2ws3ed4rf5tg',
            'password_repeat': '1qa2ws3ed4rf',
        }

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': ['Passwords are different.']}