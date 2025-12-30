# # apps/accounts/views.py

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages

# def admin_login(request):
#     """Admin login view"""
#     if request.user.is_authenticated:
#         return redirect('admin_dashboard')
    
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)
#             messages.success(request, f'Welcome back, {user.username}!')
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request, 'Invalid username or password')
    
#     return render(request, 'admin/login.html')


# def admin_logout(request):
#     """Admin logout view"""
#     logout(request)
#     messages.success(request, 'You have been logged out successfully')
#     return redirect('home')

# apps/accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def admin_login(request):
    """Admin login view"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page or dashboard
            next_page = request.GET.get('next', 'admin_dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin/login.html')


@login_required
def admin_logout(request):
    """Admin logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')