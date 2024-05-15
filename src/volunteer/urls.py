from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="volunteer"),
    path("your-opportunities/", views.your_opportunities, name="your-opportunities"),
    path("volunteer_form/", views.volunteer_form, name="volunteer_form"),
    path("register_absence/<int:registration_id>", views.volunteer_absence, name="register_absence"),
    path("stop_volunteering/<int:id>", views.stop_volunteering, name="stop_volunteering"),
    #Form Views
    path("emergency_contact_form/", views.emergency_contact_form, name="emergency_contacts_form"),
    path("volunteer_conditions_form/", views.volunteer_conditions_form, name="volunteer_conditions_form"),
    path("volunteer_address_form/", views.volunteer_address_form, name="volunteer_address_form"),
    #Form edit views
    path("emergency_contact_form/<int:contact_id>/", views.emergency_contact_form, name="emergency_contact_form"),
    path("volunteer_conditions_form/<int:condition_id>/", views.volunteer_conditions_form, name="volunteer_conditions_form"),
    path("volunteer_address_form/<int:address_id>/", views.volunteer_address_form, name="volunteer_address_form"),
    path("volunteer_supplementary_info_form/<int:supp_info_id>/", views.volunteer_supp_info_form, name="volunteer_supp_info_form"),
    #Form delete views
    path("emergency_contact_form/<int:contact_id>/delete", views.emergency_contact_form, name="emergency_contact_form", kwargs={"delete": True}),
    path("volunteer_conditions_form/<int:condition_id>/delete", views.volunteer_conditions_form, name="volunteer_conditions_form", kwargs={"delete": True}),
    path("volunteer_address_form/<int:address_id>/delete", views.volunteer_address_form, name="volunteer_address_form", kwargs={"delete": True}),
    #User views
    path("sign-up/", views.sign_up, name="sign-up"),
    path("logout/", views.user_logout, name="logout"),
]