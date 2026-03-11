# apps/public/views.py

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect

from mongoengine.queryset.visitor import Q

from apps.common_utils import (
    get_active_skill_categories,
    get_document_or_404,
    skill_sort_key,
)
from .models import (
    AboutPage,
    Blog,
    ContactPage,
    ContactSubmission,
    CoreValue,
    Education,
    Experience,
    Achievement,
    HomePage,
    Interest,
    Profile,
    Project,
    ResearchCategory,
    ResearchEntry,
    Skill,
)


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
    active_categories = get_active_skill_categories()
    category_filter = {"category__in": active_categories} if active_categories else {"category__in": []}
    featured_skills = Skill.objects.filter(is_active=True, **category_filter).order_by('-proficiency')[:4]

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
    core_values = CoreValue.objects.filter(
        Q(is_active=True) | Q(is_active__exists=False)
    )
    
    experiences = Experience.objects.filter(is_active=True).order_by("order", "-created_at")
    achievements = Achievement.objects.filter(is_active=True).order_by("order", "-created_at")
    
    latest_education = Education.objects.filter(order=0).order_by('-created_at').first()
    skill_count = Skill.objects.filter(is_active=True).count()
    research_count = ResearchEntry.objects.filter(
        Q(is_active=True) | Q(is_active__exists=False)
    ).count()
    hero_stats = [
        {
            'icon': 'bi bi-mortarboard',
            'value': latest_education.degree if latest_education else 'Education',
            'subtitle': latest_education.institution if latest_education else '',
        },
        {
            'icon': 'bi bi-code-slash',
            'value': f'{projects_count}+',
            'subtitle': 'Projects',
        },
        {
            'icon': 'bi bi-file-earmark-text',
            'value': f'{research_count}+',
            'subtitle': 'Research',
        },
        {
            'icon': 'bi bi-star',
            'value': f'{skill_count}+',
            'subtitle': 'Skills',
        },
    ]
    research_categories = ResearchCategory.objects.filter(is_active=True)
    research_data = []
    for category in research_categories:
        entries = ResearchEntry.objects.filter(category=category).filter(
            Q(is_active=True) | Q(is_active__exists=False)
        )
        research_data.append({'category': category, 'entries': entries})
    context = {
        'profile': profile,
        'about_page': about_page,
        'projects_count': projects_count,
        'blogs_count': blogs_count,
        'education': education,
        'interests': interests,
        'values_list': core_values,
        'experiences': experiences,
        'achievements': achievements,
        'core_values': core_values,
        'hero_stats': hero_stats,
        'research_data': research_data,
        'about_page_visibility': {
            'page_title': getattr(about_page, 'show_page_title', True),
            'introduction': getattr(about_page, 'show_introduction', True),
            'stats_section': getattr(about_page, 'show_stats_section', True),
            'interests': getattr(about_page, 'show_interests', True),
            'values': getattr(about_page, 'show_values', True),
            'experiences': getattr(about_page, 'show_experiences_section', True),
            'achievements': getattr(about_page, 'show_achievements_section', True),
        },
    }
    return render(request, 'public/about.html', context)

def skills(request):
    """Skills page view"""
    active_categories = get_active_skill_categories()
    category_filter = {"category__in": active_categories} if active_categories else {"category__in": []}
    all_skills_qs = Skill.objects.filter(is_active=True, **category_filter)
    all_skills = sorted(all_skills_qs, key=skill_sort_key)
    
    for skill in all_skills:
        skill.display_proficiency = skill.proficiency_percent

    # Group skills by category
    skills_by_category = {}
    for skill in all_skills:
        category = skill.category_name
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)

    # Summary cards based on categories + active skills count
    ICON_MAP = {
        "programming-languages": "bi bi-slash-lg",
        "data-science": "bi bi-graph-up",
        "web-technologies": "bi bi-browser-chrome",
        "tools-frameworks": "bi bi-gear",
    }
    skill_summaries = []
    for category in active_categories:
        count = Skill.objects.filter(category=category, is_active=True).count()
        skill_summaries.append({
            "name": category.name,
            "count": count,
            "display": f"{count}+" if count else "0",
            "icon": ICON_MAP.get(category.slug, "bi bi-star"),
        })

    home_page = HomePage.objects.first()
    context = {
        'skills_by_category': skills_by_category,
        'all_skills': all_skills,
        'skill_summaries': skill_summaries,
        'show_skills_summary': getattr(home_page, 'show_skills_summary', True),
        'show_cta_section': getattr(home_page, 'show_cta_section', True),
        'cta_title': getattr(home_page, 'cta_title', 'Interested in Working Together?'),
        'cta_description': getattr(home_page, 'cta_description', "Let's create something amazing"),
        'cta_button_text': getattr(home_page, 'cta_button_text', 'Get In Touch'),
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
    project = get_document_or_404(Project, id=id, is_active=True)
    
    # Get related projects (same tech stack or recent)
    related_projects = Project.objects.filter(is_active=True).filter(id__ne=id).order_by('-created_at')[:3]
    
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
    blog = get_document_or_404(Blog, id=id, status='published', is_active=True)
    
    # Get related blogs (same tags or recent)
    related_blogs = Blog.objects.filter(
        status='published',
        is_active=True
    ).filter(id__ne=id).order_by('-published_date')[:3]
    
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
            submission = ContactSubmission(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            submission.save()

            
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

