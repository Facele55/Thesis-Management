from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage # To upload Profile Picture
from django.urls import reverse
import datetime # To Parse input DateTime into Python Date Time Object
from django.shortcuts import render
from django.conf import settings
from djangoProject4.settings import EMAIL_HOST_USER
from . import forms
from django.core.mail import send_mail, BadHeaderError

from mainapp.models import *
from .forms import ContactForm


def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)

    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_thesises = Thesis.objects.filter(course_id=course_obj).count()

    thesis_name = []
    thesis_data = Thesis.objects.filter(course_id=student_obj.course_id)
    for subject in thesis_data:
        thesis_name.append(subject.thesis_name)
    
    context = {
        "total_thesis": total_thesises,
        "thesis_name": thesis_name
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




def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            to_email = form.cleaned_data['to_email']
            from_email = settings.EMAIL_HOST_USER  # request.user.email # form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            student_obj = Students.objects.get(admin_id=request.user.id)
            try:
                send_mail(subject, message, from_email, [to_email])
                sended_emails = SendedEmails(subject=subject, message=message, sender_id=student_obj, recipient=to_email, confirm_status=0)
                sended_emails.save()
            except BadHeaderError:
                messages.error(request, "Failed to Send email !")
                return redirect('contact')
            messages.success(request, "Email sent Successfully!")
            return redirect('contact')

    return render(request, "student_template/contact.html", {'form': form})


def sended_emails(request):
    emails = SendedEmails.objects.all()
    student = Students.objects.get(admin_id=request.user.id)
    context = {
        "emails": emails,
        "student": student
    }
    return render(request, "student_template/student_sended_emails.html", context)


