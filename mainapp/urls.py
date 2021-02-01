
from django.urls import path, include
from . import views
from .import HodViews, StaffViews, StudentViews


urlpatterns = [
    path('', views.loginPage, name="login"),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('doLogin/', views.doLogin, name="doLogin"),
    path('get_user_details/', views.get_user_details, name="get_user_details"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('admin_home/', HodViews.admin_home, name="admin_home"),
    path('add_staff/', HodViews.add_staff, name="add_staff"),
    path('add_staff_save/', HodViews.add_staff_save, name="add_staff_save"),
    path('manage_staff/', HodViews.manage_staff, name="manage_staff"),
    path('edit_staff/<staff_id>/', HodViews.edit_staff, name="edit_staff"),
    path('edit_staff_save/', HodViews.edit_staff_save, name="edit_staff_save"),
    path('delete_staff/<staff_id>/', HodViews.delete_staff, name="delete_staff"),
path('hod_sort_course/<id>/', HodViews.hod_sort_course, name="hod_sort_course"),
    path('add_student/', HodViews.add_student, name="add_student"),
    path('add_student_save/', HodViews.add_student_save, name="add_student_save"),
    path('edit_student/<student_id>', HodViews.edit_student, name="edit_student"),
    path('edit_student_save/', HodViews.edit_student_save, name="edit_student_save"),
    path('manage_student/', HodViews.manage_student, name="manage_student"),
    path('delete_student/<student_id>/', HodViews.delete_student, name="delete_student"),
    path('add_course/', HodViews.add_course, name="add_course"),
    path('add_course_save/', HodViews.add_course_save, name="add_course_save"),
    path('manage_course/', HodViews.manage_course, name="manage_course"),
    path('edit_course/<course_id>/', HodViews.edit_course, name="edit_course"),
    path('edit_course_save/', HodViews.edit_course_save, name="edit_course_save"),
    path('delete_course/<course_id>/', HodViews.delete_course, name="delete_course"),

    path('check_email_exist/', HodViews.check_email_exist, name="check_email_exist"),
    path('check_username_exist/', HodViews.check_username_exist, name="check_username_exist"),
    path('admin_profile/', HodViews.admin_profile, name="admin_profile"),
    path('admin_profile_update/', HodViews.admin_profile_update, name="admin_profile_update"),
    path('hod_received_emails/', HodViews.hod_received_emails, name="hod_received_emails"),
    path('hod_choice_approve/<result_id>/', HodViews.hod_choice_approve, name="hod_choice_approve"),
    path('hod_choice_reject/<result_id>/', HodViews.hod_choice_reject, name="hod_choice_reject"),
    path('hod_assigned_thesises/', HodViews.hod_assigned_thesises, name="hod_assigned_thesises"),

    path('hod_sort_approved/', HodViews.hod_sort_approved, name="hod_sort_approved"),
    path('hod_sort_rejected/', HodViews.hod_sort_rejected, name="hod_sort_rejected"),
    path('hod_sort_pending/', HodViews.hod_sort_pending, name="hod_sort_pending"),

    
    path('pdf_download/<int:id>', HodViews.DownloadPDF, name="pdf_download"),
    path('pdf_downloadall/', HodViews.DownloadPDFAll, name="pdf_downloadall"),
    path('thesisall/', HodViews.hod_assigned_thesisesall, name="thesisall"),


    # URLS for Staff
    path('staff_home/', StaffViews.staff_home, name="staff_home"),

    path('staff_sort_approved/', StaffViews.staff_sort_approved, name="staff_sort_approved"),
    path('staff_sort_rejected/', StaffViews.staff_sort_rejected, name="staff_sort_rejected"),
    path('staff_sort_pending/', StaffViews.staff_sort_pending, name="staff_sort_pending"),

    path('staff_profile/', StaffViews.staff_profile, name="staff_profile"),
    path('staff_profile_update/', StaffViews.staff_profile_update, name="staff_profile_update"),
    path('staff_received_emails/', StaffViews.staff_received_emails, name="staff_received_emails"),
    path('staff_choice_approve/<result_id>/', StaffViews.staff_choice_approve, name="staff_choice_approve"),
    path('staff_choice_reject/<result_id>/', StaffViews.staff_choice_reject, name="staff_choice_reject"),
    path('assigned_thesises/', StaffViews.assigned_thesises, name="assigned_thesises"),

    # URSL for Student
    path('student_home/', StudentViews.student_home, name="student_home"),
    path('student_profile/', StudentViews.student_profile, name="student_profile"),
    path('student_profile_update/', StudentViews.student_profile_update, name="student_profile_update"),
    path('sended_emails/', StudentViews.sended_emails, name="sended_emails"),
    path('student_sent_thesisemail/', StudentViews.student_sent_thesisemail, name="student_sent_thesisemail"),
    path('sendmail/', StudentViews.sendmail, name="sendmail"),
]
