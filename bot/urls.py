from django.urls import path

from bot.views import VerificationView

app_name = 'bot'

urlpatterns = [
    path('verify', VerificationView.as_view(), name='bot_verify'),
]
