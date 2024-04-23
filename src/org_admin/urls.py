from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("details/", views.details, name="details"),
    path("add_location/", views.location, name="add_location"),
    path("edit_location/<int:id>/", views.location, name="edit_location"),
    path("delete_location/<int:id>/", views.location, name="delete_location", kwargs={'delete': True}),


    path("upload_media/organisation_image/", views.upload_media, name="upload_media_organisation", kwargs={'location': 'org_media'}),
    path("upload_media/opportunity_image/<int:id>", views.upload_media, name="upload_media_opportunity", kwargs={'location': 'opportunity_media'}),

    path("delete_media/opportunity_image/<int:id>/<str:media_type>/", views.delete_media, name="delete_media_opportunity", kwargs={'location': 'opportunity_media'}),
    path("delete_media/organisation_image/<int:id>/<str:media_type>/", views.delete_media, name="delete_media_organisation", kwargs={'location': 'org_media'}),

    path("opportunities/", views.opportunity_admin, name="opportunity_admin"),
    path("opportunities/<int:id>/", views.opportunity_details_admin, name="opportunity_details"),
    path("delete_date/<int:opportunity_id>/<int:id>/", views.delete_date, name="delete_date"),
    path("add_date/<int:id>/", views.add_date, name="add_date"),

    path("volunteers/", views.volunteer_admin, name="volunteer_admin"),
]