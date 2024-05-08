from django.urls import path

from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path("<int:form_id>/", views.fill_form, name="form_detail"),
]