# apps/public/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Profile, Skill, Project, Blog
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import (
    Profile, Skill, Project, Blog,
    HomePage, AboutPage, ContactPage,
    Education, Interest, CoreValue
)
from django.db.models import Q
from django.http import JsonResponse
from .models import ContactSubmission


def home(request):
    """Home page view"""
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    try:
        home_page = HomePage.objects.first()
    except:
        home_page = None

    home_page_visibility = {
        'hero_title': getattr(home_page, 'show_hero_title', True),
        'hero_subtitle': getattr(home_page, 'show_hero_subtitle', True),
        'hero_description': getattr(home_page, 'show_hero_description', True),
        'cta_section': getattr(home_page, 'show_cta_section', True),
    }
    
    # Get counts
    projects_count = Project.objects.filter(is_active=True).count()
    blogs_count = Blog.objects.filter(status='published', is_active=True).count()
    
    # Featured skills (top 4)
    featured_skills = Skill.objects.filter(is_active=True, category__is_active=True).order_by('-proficiency')[:4]

    typing_texts = [skill.name for skill in featured_skills]
    
    # Featured projects (top 3)
    featured_projects = Project.objects.filter(is_featured=True, is_active=True)[:3]
    if featured_projects.count() < 3:
        featured_projects = Project.objects.filter(is_active=True)[:3]
    
    # Latest blogs (top 3)
    latest_blogs = Blog.objects.filter(status='published', is_active=True).order_by('-published_date')[:3]
    
    context = {
        'profile': profile,
        'home_page': home_page,
        'home_page_visibility': home_page_visibility,
        'projects_count': projects_count,
        'blogs_count': blogs_count,
        'featured_skills': featured_skills,
        'featured_projects': featured_projects,
        'latest_blogs': latest_blogs,
        'typing_texts': typing_texts,
    }
    return render(request, 'public/home.html', context)


def about(request):
    """About page view"""
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    try:
        about_page = AboutPage.objects.first()
    except:
        about_page = None
    
    projects_count = Project.objects.filter(is_active=True).count()
    blogs_count = Blog.objects.filter(status='published', is_active=True).count()
    
    # Get education entries
    education = Education.objects.all()
    
    # Get interests
    interests = Interest.objects.all()
    
    # Get core values
    core_values = CoreValue.objects.all()
    
    context = {
        'profile': profile,
        'about_page': about_page,
        'projects_count': projects_count,
        'blogs_count': blogs_count,
        'education': education,
        'interests': interests,
        'core_values': core_values,
        'about_page_visibility': {
            'page_title': getattr(about_page, 'show_page_title', True),
            'introduction': getattr(about_page, 'show_introduction', True),
            'stats_section': getattr(about_page, 'show_stats_section', True),
            'interests': getattr(about_page, 'show_interests', True),
            'values': getattr(about_page, 'show_values', True),
        },
    }
    return render(request, 'public/about.html', context)

def skills(request):
    """Skills page view"""
    all_skills = Skill.objects.filter(is_active=True, category__is_active=True).order_by('category__name', '-proficiency')
    
    # Group skills by category
    skills_by_category = {}
    for skill in all_skills:
        category = skill.category_name
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)
    
    context = {
        'skills_by_category': skills_by_category,
        'all_skills': all_skills,
    }
    return render(request, 'public/skills.html', context)


def projects(request):
    """Projects list page view"""
    all_projects = Project.objects.filter(is_active=True).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_projects = all_projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(all_projects, 6)  # 6 projects per page
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)
    
    context = {
        'projects': projects_page,
        'search_query': search_query,
    }
    return render(request, 'public/projects.html', context)


def project_detail(request, id):
    """Single project detail page view"""
    project = get_object_or_404(Project, id=id, is_active=True)
    
    # Get related projects (same tech stack or recent)
    related_projects = Project.objects.filter(is_active=True).exclude(id=id).order_by('-created_at')[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'public/project_detail.html', context)


def blog_list(request):
    """Blog list page view"""
    all_blogs = Blog.objects.filter(status='published', is_active=True).order_by('-published_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_blogs = all_blogs.filter(
            Q(title__icontains=search_query) |
            Q(preview__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Filter by tag
    tag_filter = request.GET.get('tag', '')
    if tag_filter:
        all_blogs = [blog for blog in all_blogs if tag_filter in blog.tags]
    
    # Pagination
    paginator = Paginator(all_blogs, 6)  # 6 blogs per page
    page_number = request.GET.get('page')
    blogs_page = paginator.get_page(page_number)
    
    # Get all unique tags
    all_tags = set()
    for blog in Blog.objects.filter(status='published', is_active=True):
        if blog.tags:
            all_tags.update(blog.tags)
    
    context = {
        'blogs': blogs_page,
        'search_query': search_query,
        'tag_filter': tag_filter,
        'all_tags': sorted(all_tags),
    }
    return render(request, 'public/blog_list.html', context)


def blog_detail(request, id):
    """Single blog detail page view"""
    blog = get_object_or_404(Blog, id=id, status='published', is_active=True)
    
    # Get related blogs (same tags or recent)
    related_blogs = Blog.objects.filter(
        status='published',
        is_active=True
    ).exclude(id=id).order_by('-published_date')[:3]
    
    context = {
        'blog': blog,
        'related_blogs': related_blogs,
    }
    return render(request, 'public/blog_detail.html', context)


# def contact(request):
#     """Contact page view"""
#     try:
#         profile = Profile.objects.first()
#     except:
#         profile = None
    
#     try:
#         contact_page = ContactPage.objects.first()
#     except:
#         contact_page = None
    
#     context = {
#         'profile': profile,
#         'contact_page': contact_page,
#     }
#     return render(request, 'public/contact.html', context)

def contact(request):
    """Contact page view"""
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    try:
        contact_page = ContactPage.objects.first()
    except:
        contact_page = None
    
    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate data
        if name and email and subject and message:
            # Save to database
            ContactSubmission.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Return JSON response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you! Your message has been sent successfully.'
                })
            
            # For regular form submission
            messages.success(request, 'Thank you! Your message has been sent successfully.')
            return redirect('contact')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                })
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'profile': profile,
        'contact_page': contact_page,
        'contact_page_visibility': {
            'page_header': getattr(contact_page, 'show_page_title', True) or getattr(contact_page, 'show_page_subtitle', True),
            'page_title': getattr(contact_page, 'show_page_title', True),
            'page_subtitle': getattr(contact_page, 'show_page_subtitle', True),
            'connect_section': getattr(contact_page, 'show_connect_section', True),
            'contact_info': getattr(contact_page, 'show_contact_info', True),
            'contact_form': getattr(contact_page, 'show_contact_form', True),
            'cta_section': getattr(contact_page, 'show_cta_section', True),
        },
    }
    return render(request, 'public/contact.html', context)

