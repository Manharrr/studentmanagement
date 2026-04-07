from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from student_mgmt.settings import EMAIL_HOST_USER
from students.forms import CourseForm
from students.models import Enrollment, Course
from .forms import RegisterForm, StudentForm, EnrollmentForm
User = get_user_model()



def is_admin(user):
    return user.is_superuser or user.role == 'admin'


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  

            if user.is_superuser:
                return redirect("dashboard")
            elif user.role == 'admin':
                return redirect("dashboard")
            else:
                return redirect("student_dashboard")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, "accounts/login.html", {
        'hide_navbar': True
    })


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.role = 'student'   
            user.is_staff = False   
            user.save()
            try:
                send_mail(
                    subject="Welcome to Student Management System",
                    message=f"Dear {user.username}, welcome!",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except:
                pass
            messages.success(request, "Account created successfully")
            return redirect("login")
        else:
            print("ERROR:", form.errors)
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form, "hide_navbar": True})



@login_required
def admin_base(request):
    if not is_admin(request.user):
      return redirect("login")

    total_students = User.objects.filter(role='student').count()
    total_admins = User.objects.filter(role='admin').count()
    recent_students = User.objects.filter(role='student').order_by('-date_of_join')[:5]
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()

    context = {
        'total_students': total_students,
        'total_admins': total_admins,
        'recent_students': recent_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
    }
    return render(request, "admin/dashboard/dashboard.html", context)


# admin view of stud pg
@login_required
def student_list(request):
    if not is_admin(request.user):
     return redirect("login")

    students = User.objects.filter(role='student').order_by('-date_of_join')
    query = request.GET.get('q')
    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    paginator = Paginator(students, 7)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "admin/students/list.html", {"students": page_obj, "query": query})


#  view for admin
@login_required
def student_add(request):
    if not is_admin(request.user):
        return redirect("login")

    form = StudentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.role = 'student'
        user.is_staff = False
        user.save()
        messages.success(request, "Student added successfully")
        return redirect("student_list")
    return render(request, "admin/students/form.html", {"form": form, "title": "Add Student"})



@login_required
def student_edit(request, pk):
    if not is_admin(request.user):
     return redirect("login")

    student = get_object_or_404(User, pk=pk, role='student')
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student updated successfully")
        return redirect("student_list")
    return render(request, "admin/students/form.html", {"form": form, "title": "Edit Student"})



@login_required
def student_delete(request, pk):
    if not is_admin(request.user):
     return redirect("login")

    student = get_object_or_404(User, pk=pk, role='student')
    student.delete()
    messages.success(request, "Student deleted successfully")
    return redirect("student_list")



@login_required
def enrollment_list(request):
    if not is_admin(request.user):
     return redirect("login")

    enrollments = Enrollment.objects.all().order_by('-enrolled_at')
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    if query:
        enrollments = enrollments.filter(
            Q(student__username__icontains=query) |
            Q(student__email__icontains=query) |
            Q(course__title__icontains=query)
        )
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)

    paginator = Paginator(enrollments, 7)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "admin/enrollments/list.html", {
        "enrollments": page_obj,
        "query": query,
        "status_filter": status_filter,
        "status_choices": Enrollment.STATUS_CHOICES
    })


@login_required
def enrollment_add(request):
    if not is_admin(request.user):
     return redirect("login")

    form = EnrollmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student enrolled successfully")
        return redirect("enrollment_list")
    return render(request, "admin/enrollments/form.html", {"form": form, "title": "Enroll Student"})

@login_required
def enrollment_edit(request, pk):
    if not is_admin(request.user):
     return redirect("login")

    enrollment = get_object_or_404(Enrollment, pk=pk)
    old_status = enrollment.status
    form = EnrollmentForm(request.POST or None, instance=enrollment)

    if request.method == "POST" and form.is_valid():
        updated = form.save()
        if old_status != 'In Progress' and updated.status == 'In Progress':
            try:
                send_mail(
                    subject=f" Course Approved: {updated.course.title}",
                    message=f"Hi {updated.student.username},\n\nYour enrollment for '{updated.course.title}' has been approved!\n\nYou can now start learning by logging in to your account.\n\n— Student Management Team",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[updated.student.email],
                    fail_silently=True
                )
            except:
                pass

        messages.success(request, "Enrollment updated successfully")
        return redirect("enrollment_list")

    return render(request, "admin/enrollments/form.html", {"form": form, "title": "Edit Enrollment"})


@login_required
def enrollment_delete(request, pk):
    if not is_admin(request.user):
     return redirect("login")

    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.delete()
    messages.success(request, "Enrollment deleted successfully")
    return redirect("enrollment_list")

@login_required
def admin_course_list(request):
    if not is_admin(request.user):
     return redirect("login")

    courses = Course.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    if query:
        courses = courses.filter(title__icontains=query)
    paginator = Paginator(courses, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "admin/courses/list.html", {"courses": page_obj, "query": query})



@login_required
def admin_course_add(request):
    if not is_admin(request.user):
     return redirect("login")

    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course added successfully")
        return redirect("admin_course_list")
    return render(request, "admin/courses/form.html", {"form": form, "title": "Add Course"})



@login_required
def admin_course_edit(request, pk):
    if not is_admin(request.user):
     return redirect("login")

    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course updated successfully")
        return redirect("admin_course_list")
    return render(request, "admin/courses/form.html", {"form": form, "title": "Edit Course", "course": course})


@login_required
def admin_course_delete(request, pk):
    if not is_admin(request.user):
     return redirect("login")

    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, "Course deleted successfully")
    return redirect("admin_course_list")


@login_required
def password_change_view(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        elif len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Password changed Please login again.")
            logout(request)
            return redirect("login")

    if request.user.role == 'student':
        return render(request, "student_profile/password_change.html")
    return render(request, "admin/password_change.html")

