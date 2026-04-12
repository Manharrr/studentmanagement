from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, Enrollment
from accounts.forms import StudentProfileForm

from django.contrib.auth import logout


@login_required
def Student_dashboard(request):
    if request.user.is_staff:
        return redirect("login")
    
    enrollments = Enrollment.objects.filter(
        student=request.user, 
        status__in=['In Progress', 'Completed']
    ).select_related('course')
    
    context = {
        'enrollments': enrollments,
        'enrolled_count': enrollments.count(),
        'active_count': enrollments.filter(status='In Progress').count(),
        'completed_count': enrollments.filter(status='Completed').count(),
    }
    return render(request,'student_dashboard/student_dashboard.html', context)



@login_required
def Student_profile(request):
    if request.user.is_staff:
        return redirect("login")
        
    edit_mode = request.GET.get('edit') == 'true' or request.method == 'POST'
    
    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("student_profile")
    else:
        form = StudentProfileForm(instance=request.user)
        
    return render(request, 'student_profile/student_profile.html', {'form': form, 'edit_mode': edit_mode})



@login_required
def Student_course(request):
    if request.user.is_staff:
        return redirect("login")
        
    courses = Course.objects.all()
    user_enrollments = Enrollment.objects.filter(student=request.user)
    enrollment_status = {e.course_id: e.status for e in user_enrollments}
    
    context = {
        'courses': courses,
        'enrollment_status': enrollment_status,
    }
    return render(request,'student_course/student_course.html', context)


@login_required
def student_enroll_request(request, course_id):
    if request.user.is_staff:
        return redirect("login")
        
    course = get_object_or_404(Course, id=course_id)
    
   
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': 'Pending'}
    )
    
    if created:
        messages.success(request, f"Enrollment requested for {course.title}. Status: Pending.")
    else:
        messages.info(request, f"You are already enrolled/pending for {course.title}.")
        
    return redirect("student_course")



@login_required
def watch_course(request, course_id):
    if request.user.is_staff:
        return redirect("login")
    
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    
    context = {
        'course': course,
        'enrollment': enrollment,
    }
    return render(request, 'student_course/watch_course.html', context)

@login_required
def update_course_status(request, course_id, status):
    if request.user.is_staff:
        return redirect("login")
        
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    if status == 'Completed':
        enrollment.status = Enrollment.STATUS_COMPLETED
        messages.success(request, f"Congratulations! You completed {course.title}.")
    elif status == 'Dropped':
        enrollment.status = Enrollment.STATUS_DROPPED
        messages.warning(request, f"You have dropped {course.title}.")
    
    enrollment.save()
    return redirect('student_dashboard')

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
            messages.success(request, "Password changed successfully! Please login again.")
            logout(request)
            return redirect("login")
  
    template = "student_profile/password_change.html" if request.user.role == 'student' else "admin/password_change.html"
    return render(request, template, {})
def new ():
    pass