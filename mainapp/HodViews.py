import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from django.template.loader import get_template
from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.views import View
from xhtml2pdf import pisa

from .models import *
from .forms import AddStudentForm, EditStudentForm, AddStaffForm, EditStaffForm


def admin_home(request):
    student_count = Students.objects.all().count()
    thesis_count = Thesis.objects.all().count()
    staff_count = Staffs.objects.all().count()
    email_count = SendedEmails.objects.all().count()

    # count emails for charts
    email_status_pending = SendedEmails.objects.filter(confirm_status=0).count()
    email_status_approved = SendedEmails.objects.filter(confirm_status=1).count()
    email_status_rejected = SendedEmails.objects.filter(confirm_status=2).count()

    context = {
        "student_count": student_count,
        "staff_count": staff_count,
        "email_count": email_count,
        "thesis_count": thesis_count,

        "email_status_pending": email_status_pending,
        "email_status_approved": email_status_approved,
        "email_status_rejected": email_status_rejected,
    }
    return render(request, "hod_template/home_content.html", context)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    context = {
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')


def add_staff(request):
    form = AddStaffForm()
    context = {
        "form": form
    }
    return render(request, "hod_template/add_staff_template.html", context)


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_staff')
    else:
        form = AddStaffForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      first_name=first_name, last_name=last_name, user_type=2)
                user.staffs.address = address

                user.staffs.gender = gender
                user.staffs.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Staff Added Successfully!")
                return redirect('add_staff')
            except:
                messages.error(request, "Failed to Add Staff!")
                return redirect('add_staff')
        else:
            return redirect('add_staff')


def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    # Adding Student ID into Session Variable
    request.session['staff_id'] = staff_id
    try:
        staff = Staffs.objects.get(admin=staff_id)
        form = EditStaffForm()
        # Filling the form with Data from Database
        form.fields['email'].initial = staff.admin.email
        form.fields['username'].initial = staff.admin.username
        form.fields['first_name'].initial = staff.admin.first_name
        form.fields['last_name'].initial = staff.admin.last_name
        form.fields['address'].initial = staff.address
        form.fields['gender'].initial = staff.gender

        context = {
            "id": staff_id,
            "username": staff.admin.username,
            "form": form
        }
    except Staffs.DoesNotExist:
        return redirect('manage_staff')
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        staff_id = request.session.get('staff_id')
        if staff_id == None:
            return redirect('/manage_staff')
        form = EditStaffForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=staff_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                staff_model = Staffs.objects.get(admin=staff_id)
                staff_model.address = address

                staff_model.gender = gender
                if profile_pic_url != None:
                    staff_model.profile_pic = profile_pic_url
                staff_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['staff_id']

                messages.success(request, "Staff Updated Successfully!")
                return redirect('/edit_staff/' + staff_id)
            except:
                messages.success(request, "Failed to Update Staff.")
                return redirect('/edit_staff/' + staff_id)
        else:
            return redirect('/edit_staff/' + staff_id)


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    staff1 = CustomUser.objects.get(id=staff_id)
    try:
        staff.delete()
        staff1.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)


def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address

                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except:
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id
    try:
        student = Students.objects.get(admin=student_id)
        form = EditStudentForm()
        # Filling the form with Data from Database
        form.fields['email'].initial = student.admin.email
        form.fields['username'].initial = student.admin.username
        form.fields['first_name'].initial = student.admin.first_name
        form.fields['last_name'].initial = student.admin.last_name
        form.fields['address'].initial = student.address
        form.fields['gender'].initial = student.gender

        context = {
            "id": student_id,
            "username": student.admin.username,
            "form": form
        }
    except Students.DoesNotExist:
        return redirect('manage_student')
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/' + student_id)
            except:
                messages.success(request, "Failed to Update Student.")
                return redirect('/edit_student/' + student_id)
        else:
            return redirect('/edit_student/' + student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    student1 = CustomUser.objects.get(id=student_id)
    try:
        student.delete()
        student1.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    request.session['course_id'] = course_id
    try:
        course = Courses.objects.get(id=course_id)
        context = {
            "course": course,
            "id": course_id
        }
    except Courses.DoesNotExist:
        return redirect('manage_course')
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


def hod_received_emails(request):
    rec_emails = SendedEmails.objects.all()
    context = {
        "rec_emails": rec_emails
    }
    return render(request, 'hod_template/hod_received_emails.html', context)


def hod_sort_approved(request):
    staff = Staffs.objects.all()
    rec_emails = SendedEmails.objects.filter(Q(confirm_status=1))
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'hod_template/hod_received_emails.html', context)


def hod_sort_rejected(request):
    staff = Staffs.objects.all()
    rec_emails = SendedEmails.objects.filter(Q(confirm_status=2))
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'hod_template/hod_received_emails.html', context)


def hod_sort_pending(request):
    staff = Staffs.objects.all()
    rec_emails = SendedEmails.objects.filter(Q(confirm_status=0))
    context = {
        "rec_emails": rec_emails,
        "staff": staff
    }
    return render(request, 'hod_template/hod_received_emails.html', context)


def hod_choice_approve(request, result_id):
    choice = SendedEmails.objects.get(id=result_id)
    choice.confirm_status = 1
    choice.save()
    return redirect('hod_received_emails')


def hod_choice_reject(request, result_id):
    choice = SendedEmails.objects.get(id=result_id)
    choice.confirm_status = 2
    choice.save()
    return redirect('hod_received_emails')



@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def DownloadPDF(request, id):
    thesis = Thesis.objects.get(id=id)

    template = get_template("hod_template/hod_assigned_detail.html")
    html = template.render({"thesis": thesis})

    file = open('Thesis.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                                encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')


def DownloadPDFAll(request):
    thesis = Thesis.objects.all()
    course = Courses.objects.all()

    template = get_template("hod_template/hod_assigned_all.html")
    html = template.render({"thesis": thesis, "course":  course})

    file = open('Theses_all.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                                encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')


def hod_assigned_thesises(request):
    thesis = Thesis.objects.all()
    student = Students.objects.all()
    course = Courses.objects.all()
    context = {
        "thesis": thesis,
        "student": student,
        "course": course,

    }
    return render(request, 'hod_template/hod_assigned_thesises.html', context)


def hod_sort_course(request):
    student = Students.objects.all()
    thesis = Thesis.objects.all()
    context = {
        "student": student,
        "thesis": thesis
    }
    return render(request, 'hod_template/hod_assigned_thesises.html', context)


def hod_assigned_detail(request, id):
    thesis = Thesis.objects.get(id=id)
    context = {
        "thesis": thesis,
    }
    return render(request, 'hod_template/hod_assigned_detail.html', context)


def hod_assigned_thesisesall(request):
    thesis = Thesis.objects.all()
    context = {
        "thesis": thesis,
    }
    return render(request, 'hod_template/hod_assigned_all.html', context)


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_course(request, c_id):
    # Getting Values from Ajax POST 'Fetch Student'
    c_id = request.POST.get("c_id")
    #session_year = request.POST.get("session_year")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    course_model = Courses.objects.get(id=c_id)

    #session_model = SessionYearModel.objects.get(id=session_year)

    students = Students.objects.filter(course_id=course_model.id)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in students:
        data_small = {"id": student.admin.id, "name": student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)



def staff_profile(request):
    pass


def student_profile(request):
    pass
