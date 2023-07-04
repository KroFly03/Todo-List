import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db()
class TestVerifyBotView:
    url = reverse('bot:bot_verify')

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'Authentication credentials were not provided.'}

    def test_incorrect_verification_code(self, auth_client):
        data = {'verification_code': '1234'}

        response = auth_client.patch(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'verification_code': ['Invalid verification code.']}

    def test_already_verified_user(self, auth_client, tg_user):
        tg_user.update_verification_code()

        data = {'verification_code': tg_user.verification_code}

        response = auth_client.patch(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'verification_code': ['User has already verified.']}
