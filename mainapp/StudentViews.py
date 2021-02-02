from smtplib import SMTPException

from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.template.loader import render_to_string
from django.urls import reverse
import datetime  # To Parse input DateTime into Python Date Time Object
from django.shortcuts import render
from django.conf import settings
from django.utils.functional import SimpleLazyObject

from djangoProject4.settings import EMAIL_HOST_USER
from . import forms
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from mainapp.models import *


def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
# count sent emails
    email_count = SendedEmails.objects.filter(sender_id=student_obj).count()
# If student sent email it will show as a result for assigned thesis or not
    email_status_pending = SendedEmails.objects.filter(confirm_status=0).filter(sender_id=student_obj).count()
    email_status_approved = SendedEmails.objects.filter(confirm_status=1).filter(sender_id=student_obj).count()
    email_status_rejected = SendedEmails.objects.filter(confirm_status=2).filter(sender_id=student_obj).count()

    context = {
        "email_count": email_count,
        "email_status_pending": email_status_pending,
        "email_status_approved": email_status_approved,
        "email_status_rejected": email_status_rejected,
    }
    return render(request, "student_template/student_home_template.html", context)


def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user)
    context = {
        "user": user,
        "student": student
    }
    return render(request, 'student_template/student_profile.html', context)


def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            student = Students.objects.get(admin=customuser.id)
            student.address = address
            student.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('student_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('student_profile')


def sended_emails(request):
    emails = SendedEmails.objects.all()
    staff = Staffs.objects.all()
    student = Students.objects.get(admin_id=request.user.id)
    context = {
        "emails": emails,
        "student": student,
        "staff": staff
    }
    return render(request, "student_template/student_sended_emails.html", context)


def student_sent_thesisemail(request):
    staff = Staffs.objects.all()
    context = {
        "staff": staff,
    }
    return render(request, 'student_template/student_sent_thesisemail.html', context)


#  Function for sending emails
def sendmail(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_sent_thesisemail')
    else:
        try:
            student_obj = Students.objects.get(admin_id=request.user.id)
            subject = "You have new thesis assign"
            msg = request.POST.get('thesis_id')
            to = request.POST.get('staff_em')
            text_content = 'Some text'
            html_content = '<html><body><h3>' + subject + ' </h3> Student  <strong>' + student_obj.admin.last_name\
                + ' ' + student_obj.admin.first_name + '</strong>  choose you to be a supervisor. ' \
            ' Your thesis topic will be <strong> '+ msg +' </strong>. For Apply or Reject, PLEASE Login to your account.' \
            '/or press links below <a href=" '+ request.build_absolute_uri('/staff_received_emails/') + '">'+ request.build_absolute_uri('/staff_received_emails/') +'</a> </body></html>'
            res = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [to])
            res.attach_alternative(html_content, "text/html")
            res.send()
            sended_emails = SendedEmails(subject=subject, message=msg, sender_id=student_obj, recipient=to,
                                         confirm_status=0, course_id=student_obj.course_id)
            sended_emails.save()
            messages.success(request, "Mail Sent Successfully")
        except SMTPException as e:
            messages.error(request, "There was an error sending an email: ", e)

        return redirect('student_sent_thesisemail')
