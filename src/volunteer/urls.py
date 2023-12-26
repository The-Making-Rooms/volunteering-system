from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="volunteer"),
    path("coreinfoform/", views.coreInfoForm, name="coreInfoForm")
]