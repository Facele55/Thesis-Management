from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  #  To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from mainapp.models import *


def staff_home(request):
    # Fetching All Theses under Staff
    thesis_count = Thesis.objects.filter(Q(staff_id=request.user.id)).count()
    staff_obj = Staffs.objects.filter(id=request.user.id)
    email_count = SendedEmails.objects.filter(Q(recipient=request.user.email)).count()
    # emails
    email_status_pending = SendedEmails.objects.filter(confirm_status=0).filter(Q(recipient=request.user.email)).count()
    email_status_approved = SendedEmails.objects.filter(confirm_status=1).filter(Q(recipient=request.user.email)).count()
    email_status_rejected = SendedEmails.objects.filter(confirm_status=2).filter(Q(recipient=request.user.email)).count()

    context = {
        "thesis_count": thesis_count,
        "email_count": email_count,
        "staff_obj": staff_obj,

        "email_status_pending": email_status_pending,
        "email_status_approved": email_status_approved,
        "email_status_rejected": email_status_rejected,
    }
    return render(request, "staff_template/staff_home_template.html", context)


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context = {
        "user": user,
        "staff": staff,
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        gender = request.POST.get('gender')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')


def staff_received_emails(request):
    staff = Staffs.objects.get(admin_id=request.user.id)
    rec_emails = SendedEmails.objects.all()
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'staff_template/staff_received_emails.html', context)


def staff_sort_approved(request):
    staff = Staffs.objects.get(admin_id=request.user.id)
    rec_emails = SendedEmails.objects.filter(Q(confirm_status=1))
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'staff_template/staff_received_emails.html', context)


def staff_sort_rejected(request):
    staff = Staffs.objects.get(admin_id=request.user.id)
    rec_emails = SendedEmails.objects.filter(Q(confirm_status=2))
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'staff_template/staff_received_emails.html', context)


def staff_sort_pending(request):
    staff = Staffs.objects.get(admin_id=request.user.id)
    rec_emails = SendedEmails.objects.filter(Q(confirm_status=0))
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'staff_template/staff_received_emails.html', context)


def staff_choice_approve(request, result_id):
    staff = CustomUser.objects.get(id=request.user.id)
    choice = SendedEmails.objects.get(id=result_id)
    choice.confirm_status = 1
    choice.save()
    thes = Thesis(thesis_name=choice.message, staff_id=staff, author_id=choice.sender_id, course_id=choice.course_id)
    thes.save()
    return redirect('staff_received_emails')


def staff_choice_reject(request, result_id):
    choice = SendedEmails.objects.get(id=result_id)
    choice.confirm_status = 2
    choice.save()
    return redirect('staff_received_emails')


def assigned_thesises(request):
    thesis = Thesis.objects.all()
    staff = Staffs.objects.get(admin_id=request.user.id)
    context = {
        "thesis": thesis,
        "staff": staff
    }
    return render(request, 'staff_template/assigned_thesises.html', context)
