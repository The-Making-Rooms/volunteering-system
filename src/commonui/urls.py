from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.index, name="home"),
    path("authenticate", views.authenticate_user, name="login"),
    path("create_account", views.create_account, name="create_account")
]