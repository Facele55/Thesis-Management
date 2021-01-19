from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json


from mainapp.models import *


def staff_home(request):
    # Fetching All Students under Staff
    thesises = Thesis.objects.filter(staff_id=request.user.id)

    thesis_count = thesises.count()

    # Fetch
    thesis_list = []
    for thesis in thesises:
        thesis_list.append(thesis.thesis_name)

    staff = Staffs.objects.get(admin=request.user.id)



    context = {
        "thesis_count": thesis_count,
        "thesis_list": thesis_list,
    }
    return render(request, "staff_template/staff_home_template.html", context)


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_students(request):
    # Getting Values from Ajax POST 'Fetch Student'
    thesis_id = request.POST.get("thesis")
    session_year = request.POST.get("session_year")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    thesis_model = Thesis.objects.get(id=thesis_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    students = Students.objects.filter(course_id=thesis_model.course_id, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in students:
        data_small = {"id": student.admin.id, "name": student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context = {
        "user": user,
        "staff": staff
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


def staff_choice_approve(request, result_id):
    staff = CustomUser.objects.get(id=request.user.id)
    choice = SendedEmails.objects.get(id=result_id)
    choice.confirm_status = 1
    choice.save()
    thes = Thesis(thesis_name=choice.message, staff_id=staff, author_id=choice.sender_id)
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
