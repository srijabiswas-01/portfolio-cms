# # apps/admin_panel/urls.py

# from django.urls import path
# from . import views

# urlpatterns = [
#     # Dashboard
#     path('dashboard/', views.dashboard, name='admin_dashboard'),
    
#     # Blog Management
#     path('blogs/', views.blogs_list, name='admin_blogs_list'),
#     path('blogs/new/', views.blog_editor, name='admin_blog_editor'),
#     path('blogs/<int:id>/edit/', views.blog_edit, name='admin_blog_edit'),
#     path('blogs/<int:id>/delete/', views.blog_delete, name='admin_blog_delete'),
    
#     # Project Management
#     path('projects/', views.project_manager, name='admin_project_manager'),
#     path('projects/new/', views.project_form, name='admin_project_form'),
#     path('projects/<int:id>/edit/', views.project_edit, name='admin_project_edit'),
#     path('projects/<int:id>/delete/', views.project_delete, name='admin_project_delete'),
    
#     # Skills Management
#     path('skills/', views.skills_manager, name='admin_skills_manager'),
#     path('skills/new/', views.skill_create, name='admin_skills_create'),
#     path('skills/<int:id>/edit/', views.skill_edit, name='admin_skills_edit'),
#     path('skills/<int:id>/delete/', views.skill_delete, name='admin_skills_delete'),
    
#     # Profile Management
#     path('profile/', views.profile_manager, name='admin_profile_manager'),
# ]


# apps/admin_panel/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    
    # Page Content Management
    path('pages/home/', views.home_page_manager, name='admin_home_page_manager'),
    path('pages/about/', views.about_page_manager, name='admin_about_page_manager'),
    path('pages/contact/', views.contact_page_manager, name='admin_contact_page_manager'),
    
    # Education Management
    path('pages/about/education/create/', views.education_create, name='admin_education_create'),
    path('pages/about/education/<int:id>/edit/', views.education_edit, name='admin_education_edit'),
    path('pages/about/education/<int:id>/delete/', views.education_delete, name='admin_education_delete'),
    
    # Interest Management
    path('pages/about/interests/create/', views.interest_create, name='admin_interest_create'),
    path('pages/about/interests/<int:id>/edit/', views.interest_edit, name='admin_interest_edit'),
    path('pages/about/interests/<int:id>/delete/', views.interest_delete, name='admin_interest_delete'),
    
    # Core Values Management
    path('pages/about/values/create/', views.value_create, name='admin_value_create'),
    path('pages/about/values/<int:id>/edit/', views.value_edit, name='admin_value_edit'),
    path('pages/about/values/<int:id>/delete/', views.value_delete, name='admin_value_delete'),
    
    # Blog Management
    path('blogs/', views.blogs_list, name='admin_blogs_list'),
    path('blogs/new/', views.blog_editor, name='admin_blog_editor'),
    path('blogs/<int:id>/edit/', views.blog_edit, name='admin_blog_edit'),
    path('blogs/<int:id>/delete/', views.blog_delete, name='admin_blog_delete'),
    
    # Project Management
    path('projects/', views.project_manager, name='admin_project_manager'),
    path('projects/new/', views.project_form, name='admin_project_form'),
    path('projects/<int:id>/edit/', views.project_edit, name='admin_project_edit'),
    path('projects/<int:id>/delete/', views.project_delete, name='admin_project_delete'),
    
    # Skills Management
    path('skills/', views.skills_manager, name='admin_skills_manager'),
    path('skills/<int:id>/toggle-active/', views.skill_toggle_active, name='admin_skill_toggle_active'),
    path('skills/new/', views.skill_create, name='admin_skills_create'),
    path('skills/<int:id>/edit/', views.skill_edit, name='admin_skills_edit'),
    path('skills/<int:id>/delete/', views.skill_delete, name='admin_skills_delete'),
    path('skills/categories/manage/', views.skill_category_manage, name='admin_skill_category_manage'),
    path('skills/categories/<int:id>/toggle-active/', views.skill_category_toggle_active, name='admin_skill_category_toggle_active'),
    path('skills/categories/<int:id>/delete/', views.skill_category_delete, name='admin_skill_category_delete'),
    
    # Profile Management
    path('profile/', views.profile_manager, name='admin_profile_manager'),
    path('contact-submissions/', views.contact_submissions, name='admin_contact_submissions'),
    path('contact-submissions/<int:id>/', views.contact_submission_detail, name='admin_contact_submission_detail'),
    path('contact-submissions/<int:id>/delete/', views.contact_submission_delete, name='admin_contact_submission_delete'),
    path('contact-submissions/<int:id>/mark-read/', views.contact_submission_mark_read, name='admin_contact_submission_mark_read'),
    path('contact-submissions/bulk-action/', views.contact_submissions_bulk_action, name='admin_contact_submissions_bulk_action'),
]
