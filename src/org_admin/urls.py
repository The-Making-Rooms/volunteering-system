"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard_index, name="index"),
    path("details/", views.details, name="details"),
    path("upload_organisation_logo/", views.upload_organisation_logo, name="upload_organisation_logo"),
    path("sign_in/", views.sign_in, name="sign_in"),
    #path("sign_out/", views.sign_out, name="sign_out"),
    
    path("password_reset_sent", views.password_reset_sent, name="password_reset_sent"),
    path("password_reset/", views.ResetPasswordView.as_view(), name="reset_password"),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='org_admin/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='org_admin/password_reset_complete.html'),
         name='password_reset_complete'),
    
    path("links/", views.org_links, name="add_link"),
    path("communication/", views.get_org_chats, name="communication_admin"),
    path("communication/preload/<int:preload_chat_id>/", views.get_org_chats, name="communication_admin"),
    path("communication/<int:chat_id>/", views.get_chat_content, name="communication_admin"),
    
    path("profile/", views.profile, name="profile"),
    path("change_password/", views.change_password, name="reset_password"),
    path("toggle_message_on_email/", views.toggle_message_on_email, name="toggle_message_on_email"),
    path("logout/", views.logout_view, name="logout"),
    
    path("upload_icons/", views.upload_icons, name="upload_icons"),
    path("icons/", views.icons, name="icons"),
    
    path("export/", views.export_all_orgs_zip, name="export"),
    
    path("location/", views.add_location_by_id, name="locations"),
    path("delete_location/<int:location_id>/", views.delete_org_location, name="delete_location"),
    
    path("supplementary_info/", views.supplementary_info, name="supplementary_info"),
    path("supplementary_info/<int:org_id>/", views.supplementary_info, name="supplementary_info"),
    path("supplementary_info/delete/<int:id>/", views.delete_supplementary_info, name="delete_supplementary_info"),
    
    path("automated_message/", views.automated_messages, name="automated_messages"),
    path("automated_message/<int:id>/", views.automated_messages, name="automated_messages"),
    
    path("manage_badge/", views.manage_badge, name="manage_badge"),
    path("manage_badge/<int:badge_id>/", views.manage_badge, name="manage_badge"),
    path("manage_badge/delete/<int:badge_id>/", views.manage_badge, name="manage_badge", kwargs={'delete': True}),
    path("manage_badge/add/<int:organisation_id>/", views.manage_badge, name="manage_badge"),
    
    path("forms/", views.forms, name="forms"),
    path("forms/create/", views.create_form, name="create_form"),
    path("forms/<int:form_id>/", views.form_detail, name="form_detail"),
    path("forms/responses/<int:form_id>/", views.get_responses, name="form_responses"),
    path("forms/response/<int:response_id>/", views.get_response, name="form_responses"),
    path("forms/download/<int:form_id>/", views.download_responses_CSV, name="download_response"),
    path("forms/download_anonymous/<int:form_id>/", views.download_responses_CSV, kwargs={'anonymous':True}, name="download_response"),
    path("forms/assign_form/", views.assign_form, name="assign_form"),
    path("forms/assign_form_org/", views.assign_form_org, name="assign_form"),
    path("forms/<int:form_id>/update/", views.update_form, name="update_form"),
    path("forms/delete/<int:form_id>/", views.delete_form, name="delete_form"),
    path("forms/<int:form_id>/add_multi_choice/", views.add_multi_choice, name="add_multi_choice"),
    path("forms/<int:form_id>/add_question/", views.add_question, name="add_question"),
    path("forms/<int:question_id>/duplicate_question/", views.duplicate_question, name="duplicate_question"),
    path("forms/<int:form_id>/add_boolean/", views.add_question, name="add_question", kwargs={'boolean': True}),
    path("forms/<int:question_id>/save/", views.save_question, name="save_question"),
    path("forms/<int:question_id>/delete/", views.delete_question, name="delete_question"),
    path("forms/<int:question_id>/add_option/", views.add_option, name="add_option"),
    path("forms/<int:option_id>/delete_option/", views.delete_option, name="delete_option"),
    path("forms/<int:question_id>/move_up/", views.move_question_down, name="move_up"),
    path("forms/<int:question_id>/move_down/", views.move_question_up, name="move_down"),
    
    path("upload_organisation_logo/<int:organisation_id>/", views.upload_organisation_logo, name="upload_organisation_logo"),
    path("organisations/<int:organisation_id>/", views.details, name="organisation_details"),
    path("organisations/manage_section/new/<int:organisation_id>/", views.org_create_new_section, name="opportunity_section_manage"),
    path("organisations/manage_section/delete/<int:section_id>/", views.org_delete_section, name="opportunity_section_delete"),
    path("organisations/manage_section/edit/<int:section_id>/", views.org_edit_section, name="opportunity_section_manage"),
    path("organisations/manage_section/move_up/<int:section_id>/", views.org_move_section_up, name="opportunity_section_manage"),
    path("organisations/manage_section/move_down/<int:section_id>/", views.org_move_section_down, name="opportunity_section_manage"),
    
    
    path("links/<int:organisation_id>/", views.org_links, name="add_link"),
    path("location/<int:organisation_id>/", views.add_location_by_id, name="locations"),
    path("upload_media/organisation_image/<int:organisation_id>/", views.upload_media, name="upload_media_organisation", kwargs={'location': 'org_media'}),

    path("upload_media/organisation_image/", views.upload_media, name="upload_media_organisation", kwargs={'location': 'org_media'}),
    path("upload_media/opportunity_image/<int:id>", views.upload_media, name="upload_media_opportunity", kwargs={'location': 'opportunity_media'}),

    path("delete_media/opportunity_image/<int:id>/<str:media_type>/", views.delete_media, name="delete_media_opportunity", kwargs={'location': 'opportunity_media'}),
    path("delete_media/organisation_image/<int:id>/<str:media_type>/", views.delete_media, name="delete_media_organisation", kwargs={'location': 'org_media'}),

    path("opportunities/", views.opportunity_admin, name="opportunity_admin", ),
    path("opportunities/filter/", views.get_filtered_opportunities, name="opportunity_admin", ),
    path("opportunities/<int:id>/", views.opportunity_details, name="opportunity_details", kwargs={'index': True}),
    path("opportunities/<int:id>/<str:tab_name>/", views.opportunity_details, name="opportunity_details"),
    path("opportunities/details/<int:id>/", views.opportunity_details, name="opportunity_details"),
    path("opportunities/sections/<int:id>/", views.opportunity_sections, name="opportunity_details"),
    path("opportunities/benefits/<int:id>/", views.opportunity_benefits, name="opportunity_benefits"),
    
    path("opportunities/tags/<int:opportunity_id>/", views.tag_details, name="manage_benefit"),
    path("opportunities/manage_tag/<int:opportunity_id>/", views.add_tag, name="manage_benefit"),
    path("opportunities/manage_tag/delete/<int:opportunity_id>/<int:linked_tag_id>/", views.add_tag, name="manage_benefit", kwargs={'delete': True}),
    
    path("opportunities/manage_section/new/<int:opportunity_id>/", views.create_new_section, name="opportunity_section_manage"),
    path("opportunities/manage_section/delete/<int:section_id>/", views.delete_section, name="opportunity_section_delete"),
    path("opportunities/manage_section/edit/<int:section_id>/", views.edit_section, name="opportunity_section_manage"),
    path("opportunities/manage_section/move_up/<int:section_id>/", views.move_section_up, name="opportunity_section_manage"),
    path("opportunities/manage_section/move_down/<int:section_id>/", views.move_section_down, name="opportunity_section_manage"),
    
    
    path("opportunities/supp_info/<int:opp_id>/", views.opportunity_supplementary_info, name="opportunity_supplementary_info"),
    path("opportunities/supp_info/delete/<int:supp_id>/", views.delete_info_req, name="delete_supp_info_requirement"),
    path("opportunities/supp_info/assign/", views.opportunity_supplementary_info, name="opportunity_supplementary_info"),
    
    path("opportunities/manage_benefit/<int:opportunity_id>/", views.manage_benefit, name="manage_benefit"),
    path("opportunities/manage_benefit/edit/<int:benefit_id>/", views.manage_benefit, name="manage_benefit"),
    path("opportunities/manage_benefit/delete/<int:benefit_id>/", views.manage_benefit, name="manage_benefit", kwargs={'delete': True}),
    
    path("opportunities/locations/<int:id>/", views.opportunity_locations, name="opportunity_locations"),
    path("opportunities/manage_location/delete/<int:location_id>/", views.delete_opportunity_location, name="manage_opportunity_location"),
    path("opportunities/manage_location/add/<int:opportunity_id>/", views.add_location_by_id, name="manage_opportunity_location"),
    
    path("opportunities/registrations/<int:id>/", views.opportunity_registrations, name="opportunity_registrations"),
    path("registrations/", views.opportunity_registrations, name="opportunity_registrations"),
    path("opportunities/registrations/set_status/", views.set_selected_registration_status, name="set_selected_registration_status"),
    path("opportunities/registrations/get_registration_table/", views.get_registration_table, name="get_registration_table"),
    
    path("mentoring/", views.get_mentees, name="mentoring"),
    path("mentoring/<int:mentee_id>/", views.manage_mentee, name="mentee_manage"),
    path("mentoring/create/<int:volunteer_id>/", views.create_mentee, name="create_mentee"),
    path("mentoring/log_hours/<int:mentee_id>/", views.log_hours, name="log_hours"),
    path("mentoring/add_note/<int:mentee_id>/", views.add_note, name="add_note"),
    path("mentoring/edit_session/<int:session_id>/", views.edit_hours, name="edit_hours"),
    path("mentoring/delete_session/<int:session_id>/", views.delete_hours, name="delete_hours"),
    path("mentoring/fill_mentee_start_form/<int:mentee_id>/", views.fill_mentee_form, name="fill_mentee_form_start", kwargs={'start_end': 'start'}),
    path("mentoring/fill_mentee_end_form/<int:mentee_id>/", views.fill_mentee_form, name="fill_mentee_form_end", kwargs={'start_end': 'end'}),
     
    
    path("admin_management/", views.get_admins, name="admin_management"),
    path("admin_management/delete/<int:admin_id>/", views.delete_admin, name="delete_admin"),
    path("admin_management/superuser/", views.add_super_user, name="add_superuser"),
    
    path("opportunities/schedule/<int:id>/", views.manage_schedule, name="opportunity_schedule"),
    path("delete_date/<int:opportunity_id>/<int:id>/", views.delete_date, name="delete_date"),
    path("add_date/<int:id>/", views.add_date, name="add_date"),
    
    path("opportunities/add/", views.create_new_opportunity, name="add_opportunity"),
    path("opportunities/delete/<int:id>/", views.delete_opportunity, name="delete_opportunity"),
    
    path("opportunities/gallery/<int:id>/", views.opportunity_gallery, name="opportunity_gallery"),
    
    path("volunteers/", views.volunteer_admin, name="volunteer_admin"),
    path("volunteers/chat/<int:volunteer_id>/", views.create_volunteer_chat, name="volunteer_chat"),
    path("volunteers/<int:id>/", views.volunteer_details_admin, name="volunteer_details"),
    
    
    path("create_new_organisation/", views.create_new_organisation, name="create_new_organisation"),
    
    path("benefits/", views.benefits_index, name="benefits_index"),
    path("benefits/add/", views.add_benefit, name="add_benefit"),
    path("benefits/<int:benefit_id>/", views.benefit_crud, name="benefit_crud"),
    path("benefits/<int:benefit_id>/delete/", views.delete_benefit, name="benefit_delete"),
    path("benefits/select_opportunity/", views.select_opportunity, name="select_opportunity"),
    path("benefits/add_to_opportunity/", views.add_benefit_to_opportunity, name="add_benefit_to_opportunity"),
    
    path("benefits/unlink/<int:link_id>/<int:opportunity_id>/", views.unlink_benefit, name="unlink_benefit_inplace"),
    path("benefits/<int:benefit_id>/<int:opportunity_id>/", views.benefit_crud, name="benefit_crud_inplace"),
    path("benefits/add/<int:opportunity_id>/", views.add_benefit, name="add_benefit_inplace"),
    
    path("additional_information/", views.additional_information, name="additional_information"),
     path("additional_information/<int:id>/delete/", views.delete_additional_info, name="delete_additional_info"),
     path("additional_information/add/", views.add_additional_info, name="add_additional_info"),
     path("additional_information/<int:id>/edit/", views.edit_additional_info, name="edit_additional_info"),
     
     path("dashboard/", views.dashboard_index, name="dashboard"),
     path("dashboard/<int:organisation_id>/", views.dashboard_index, name="dashboard_organisation"),
     
     path("email_portal/", views.email_portal_index, name="email_portal_index"),
     path("email_portal/save_draft/", views.save_email_draft, name="save_email_draft"),
     path("email_portal/new_draft/", views.edit_email_draft, name="new_email_draft"),
     path("email_portal/edit_draft/<int:draft_id>/", views.edit_email_draft, name="edit_email_draft"),
     path("email_portal/preview_draft/<int:draft_id>/", views.preview_email, name="preview_email"),
     path("email_portal/send_draft/<int:draft_id>/", views.send_email_draft, name="send_email_draft"),
     path("email_portal/send_draft/<int:draft_id>/<str:confirm_id>/", views.send_email_draft, name="send_email_draft"),
     path("email_portal/duplicate_draft/<int:draft_id>/", views.duplicate_email_draft, name="duplicate_email_draft"),
     
     path("email_portal/delete_draft/<int:draft_id>/", views.delete_email_draft, name="delete_email_draft"),
     path("email_portal/view_draft/<int:draft_id>/", views.view_email_detail, name="view_email_detail"),
     
     path("superforms/", views.superforms, name="superforms"),
     path("superforms/new/", views.new_superform, name="new_superform"),
    
    #path("utils/convert_old_schema/", views.convert_old_schema, name="convert_old_schema"),
    #path("utils/set_usernames_lowercase/", views.utils_set_emails_lower, name="set_usernames_lowercase"),
    #path("utils/gen_random_passwords/", views.utils_set_random_password, name="gen_random_passwords"),
    #path("utils/data_import/", views.data_import, name="data_import"),
    #path("utils/fix_benefit_orgs/", views.utils_set_benefit_org, name="fix_benefit_rogs"),
    #path("utils/fix_festival_followers/", views.utils_fix_festival_followers, name="fix_festival_followers"),
    #path("utils/utils_fix_organisation_interests/", views.utils_fix_organisation_interests, name="utils_fix_organisation_interests"),
    
    path("reporting/", views.reporting, name="reporting"),
]