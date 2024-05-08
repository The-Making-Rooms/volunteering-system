from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("details/", views.details, name="details"),
    path("upload_organisation_logo/", views.upload_organisation_logo, name="upload_organisation_logo"),
    path("sign_in/", views.sign_in, name="sign_in"),
    #path("sign_out/", views.sign_out, name="sign_out"),
    path("links/", views.org_links, name="add_link"),
    path("location/", views.add_location_by_id, name="locations"),
    path("delete_location/<int:location_id>/", views.delete_org_location, name="delete_location"),
    
    path("forms/", views.forms, name="forms"),
    path("forms/create/", views.create_form, name="create_form"),
    path("forms/<int:form_id>/", views.form_detail, name="form_detail"),
    path("forms/<int:form_id>/add_multi_choice/", views.add_multi_choice, name="add_multi_choice"),
    path("forms/<int:form_id>/add_question/", views.add_question, name="add_question"),
    path("forms/<int:form_id>/add_boolean/", views.add_question, name="add_question", kwargs={'boolean': True}),
    path("forms/<int:question_id>/save/", views.save_question, name="save_question"),
    path("forms/<int:question_id>/delete/", views.delete_question, name="delete_question"),
    path("forms/<int:question_id>/add_option/", views.add_option, name="add_option"),
    path("forms/<int:option_id>/delete_option/", views.delete_option, name="delete_option"),
    
    path("upload_organisation_logo/<int:organisation_id>/", views.upload_organisation_logo, name="upload_organisation_logo"),
    path("organisations/<int:organisation_id>/", views.details, name="organisation_details"),
    path("links/<int:organisation_id>/", views.org_links, name="add_link"),
    path("location/<int:organisation_id>/", views.add_location_by_id, name="locations"),
    path("upload_media/organisation_image/<int:organisation_id>/", views.upload_media, name="upload_media_organisation", kwargs={'location': 'org_media'}),

    path("upload_media/organisation_image/", views.upload_media, name="upload_media_organisation", kwargs={'location': 'org_media'}),
    path("upload_media/opportunity_image/<int:id>", views.upload_media, name="upload_media_opportunity", kwargs={'location': 'opportunity_media'}),

    path("delete_media/opportunity_image/<int:id>/<str:media_type>/", views.delete_media, name="delete_media_opportunity", kwargs={'location': 'opportunity_media'}),
    path("delete_media/organisation_image/<int:id>/<str:media_type>/", views.delete_media, name="delete_media_organisation", kwargs={'location': 'org_media'}),

    path("opportunities/", views.opportunity_admin, name="opportunity_admin", ),
    path("opportunities/<int:id>/", views.opportunity_details, name="opportunity_details", kwargs={'index': True}),
    path("opportunities/<int:id>/<str:tab_name>/", views.opportunity_details, name="opportunity_details"),
    path("opportunities/details/<int:id>/", views.opportunity_details, name="opportunity_details"),
    path("opportunities/benefits/<int:id>/", views.opportunity_benefits, name="opportunity_benefits"),
    path("opportunities/manage_tag/<int:opportunity_id>/", views.add_tag, name="manage_benefit"),
    path("opportunities/manage_tag/delete/<int:opportunity_id>/<int:linked_tag_id>/", views.add_tag, name="manage_benefit", kwargs={'delete': True}),
    
    path("opportunities/manage_benefit/<int:opportunity_id>/", views.manage_benefit, name="manage_benefit"),
    path("opportunities/manage_benefit/edit/<int:benefit_id>/", views.manage_benefit, name="manage_benefit"),
    path("opportunities/manage_benefit/delete/<int:benefit_id>/", views.manage_benefit, name="manage_benefit", kwargs={'delete': True}),
    
    path("opportunities/locations/<int:id>/", views.opportunity_locations, name="opportunity_locations"),
     path("opportunities/manage_location/delete/<int:location_id>/", views.delete_opportunity_location, name="manage_opportunity_location"),
    path("opportunities/manage_location/add/<int:opportunity_id>/", views.add_location_by_id, name="manage_opportunity_location"),
    
    
    path("opportunities/schedule/<int:id>/", views.manage_schedule, name="opportunity_schedule"),
    path("delete_date/<int:opportunity_id>/<int:id>/", views.delete_date, name="delete_date"),
    path("add_date/<int:id>/", views.add_date, name="add_date"),
    
    path("opportunities/add/", views.create_new_opportunity, name="add_opportunity"),
    path("opportunities/delete/<int:id>/", views.delete_opportunity, name="delete_opportunity"),
    
    path("opportunities/gallery/<int:id>/", views.opportunity_gallery, name="opportunity_gallery"),
    
    path("volunteers/", views.volunteer_admin, name="volunteer_admin"),
    path("volunteers/<int:id>/", views.volunteer_details_admin, name="volunteer_details"),
    
    path("communications/", views.chats, name="communication_admin"),
    path("communications/<int:id>/", views.chat, name="communication_details"),
    
    
]