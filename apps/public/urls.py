# apps/public/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile-image/', views.profile_image, name='profile_image'),
    path('resume/', views.resume_page, name='resume'),
    path('resume/file/', views.resume_file, name='resume_file'),
    path('resume/download/', views.resume_download, name='resume_download'),
    path('about/', views.about, name='about'),
    path('skills/', views.skills, name='skills'),
    path('projects/', views.projects, name='projects'),
    path('certifications/', views.certifications, name='certifications'),
    path('projects/<str:id>/image/', views.project_image, name='project_image'),
    path('projects/<str:id>/', views.project_detail, name='project_detail'),
    path('blog/', views.blog_list, name='blogs'),
    path('blog/<str:id>/cover/', views.blog_cover, name='blog_cover'),
    path('blog/<str:id>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
]
