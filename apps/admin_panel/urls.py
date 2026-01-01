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
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='admin_dashboard', permanent=False)),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    
    # Page Content Management
    path('pages/home/', views.home_page_manager, name='admin_home_page_manager'),
    path('pages/about/', views.about_page_manager, name='admin_about_page_manager'),
    path('pages/contact/', views.contact_page_manager, name='admin_contact_page_manager'),
    
    # Education Management
    path('pages/about/education/create/', views.education_create, name='admin_education_create'),
    path('pages/about/education/<str:id>/edit/', views.education_edit, name='admin_education_edit'),
    path('pages/about/education/<str:id>/delete/', views.education_delete, name='admin_education_delete'),
    path('pages/about/education/<str:id>/toggle-active/', views.education_toggle_active, name='admin_education_toggle_active'),
    
    # Interest Management
    path('pages/about/interests/create/', views.interest_create, name='admin_interest_create'),
    path('pages/about/interests/<str:id>/edit/', views.interest_edit, name='admin_interest_edit'),
    path('pages/about/interests/<str:id>/delete/', views.interest_delete, name='admin_interest_delete'),
    path('pages/about/interests/<str:id>/toggle-active/', views.interest_toggle_active, name='admin_interest_toggle_active'),
    
    # Core Values Management
    path('pages/about/values/create/', views.value_create, name='admin_value_create'),
    path('pages/about/values/<str:id>/edit/', views.value_edit, name='admin_value_edit'),
    path('pages/about/values/<str:id>/delete/', views.value_delete, name='admin_value_delete'),
    path('pages/about/values/<str:id>/toggle-active/', views.value_toggle_active, name='admin_value_toggle_active'),
    path('pages/about/research-categories/create/', views.research_category_create, name='admin_research_category_create'),
    path('pages/about/research-categories/<str:id>/edit/', views.research_category_edit, name='admin_research_category_edit'),
    path('pages/about/research-categories/<str:id>/delete/', views.research_category_delete, name='admin_research_category_delete'),
    path('pages/about/research-categories/<str:id>/toggle-active/', views.research_category_toggle_active, name='admin_research_category_toggle_active'),
    path('pages/about/research-entries/create/', views.research_entry_create, name='admin_research_entry_create'),
    path('pages/about/research-entries/<str:id>/edit/', views.research_entry_edit, name='admin_research_entry_edit'),
    path('pages/about/research-entries/<str:id>/toggle-active/', views.research_entry_toggle_active, name='admin_research_entry_toggle_active'),
    path('pages/about/research-entries/<str:id>/delete/', views.research_entry_delete, name='admin_research_entry_delete'),
    # Stats cards
    # Blog Management
    path('blogs/', views.blogs_list, name='admin_blogs_list'),
    path('blogs/new/', views.blog_editor, name='admin_blog_editor'),
    path('blogs/<str:id>/edit/', views.blog_edit, name='admin_blog_edit'),
    path('blogs/<str:id>/delete/', views.blog_delete, name='admin_blog_delete'),
    
    # Project Management
    path('projects/', views.project_manager, name='admin_project_manager'),
    path('projects/new/', views.project_form, name='admin_project_form'),
    path('projects/<str:id>/edit/', views.project_edit, name='admin_project_edit'),
    path('projects/<str:id>/delete/', views.project_delete, name='admin_project_delete'),
    
    # Skills Management
    path('skills/', views.skills_manager, name='admin_skills_manager'),
    path('skills/<str:id>/toggle-active/', views.skill_toggle_active, name='admin_skill_toggle_active'),
    path('skills/new/', views.skill_create, name='admin_skills_create'),
    path('skills/<str:id>/edit/', views.skill_edit, name='admin_skills_edit'),
    path('skills/<str:id>/delete/', views.skill_delete, name='admin_skills_delete'),
    path('skills/categories/manage/', views.skill_category_manage, name='admin_skill_category_manage'),
    path('skills/categories/<str:id>/toggle-active/', views.skill_category_toggle_active, name='admin_skill_category_toggle_active'),
    path('skills/categories/<str:id>/delete/', views.skill_category_delete, name='admin_skill_category_delete'),
    
    # Profile Management
    path('profile/', views.profile_manager, name='admin_profile_manager'),
    path('contact-submissions/', views.contact_submissions, name='admin_contact_submissions'),
    path('contact-submissions/<str:id>/', views.contact_submission_detail, name='admin_contact_submission_detail'),
    path('contact-submissions/<str:id>/delete/', views.contact_submission_delete, name='admin_contact_submission_delete'),
    path('contact-submissions/<str:id>/mark-read/', views.contact_submission_mark_read, name='admin_contact_submission_mark_read'),
    path('contact-submissions/bulk-action/', views.contact_submissions_bulk_action, name='admin_contact_submissions_bulk_action'),
]
