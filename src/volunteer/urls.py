from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="volunteer"),
    path("coreinfoform/", views.coreInfoForm, name="coreInfoForm"),
    path("emergency-contact/", views.emergencyContactForm, name="emergency-contact"),
    path("emergency-contact-form", views.emergencyContactInput, name="emergency-contact-form"),
]