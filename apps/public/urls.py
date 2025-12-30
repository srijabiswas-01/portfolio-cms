# apps/public/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('skills/', views.skills, name='skills'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:id>/', views.project_detail, name='project_detail'),
    path('blog/', views.blog_list, name='blogs'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
]