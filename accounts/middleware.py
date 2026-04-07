from django.shortcuts import redirect

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            is_admin = user.is_superuser or user.role == 'admin'

            if is_admin and request.path.startswith('/student_dashboard'):
                return redirect('dashboard')

            if user.role == 'student' and request.path.startswith('/dashboard'):
                return redirect('student_dashboard')

        response = self.get_response(request)
        return response