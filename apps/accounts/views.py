# apps/accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token
from django.http import JsonResponse


@never_cache
@require_GET
def login_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})

@never_cache
def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(reverse('admin_dashboard'))
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin/login.html')


def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')
