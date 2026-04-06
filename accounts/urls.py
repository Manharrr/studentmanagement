
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
 
urlpatterns = [
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.admin_base, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('students/delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/add/', views.enrollment_add, name='enrollment_add'),
    path('enrollments/edit/<int:pk>/', views.enrollment_edit, name='enrollment_edit'),
    path('enrollments/delete/<int:pk>/', views.enrollment_delete, name='enrollment_delete'),
    path('courses/', views.admin_course_list, name='admin_course_list'),
    path('courses/add/', views.admin_course_add, name='admin_course_add'),
    path('courses/edit/<int:pk>/', views.admin_course_edit, name='admin_course_edit'),
    path('courses/delete/<int:pk>/', views.admin_course_delete, name='admin_course_delete'),
    
     path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/forgot_password.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/forgot-password/done/'
    ), name='password_reset'),
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/forgot_password_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('password-change/', views.password_change_view, name='password_change')
]


