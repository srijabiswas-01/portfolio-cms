from django.urls import path

from . import views


urlpatterns = [
    path("chat/", views.chat, name="assistant_chat"),
    path("clear/", views.clear_history, name="assistant_clear"),
]
