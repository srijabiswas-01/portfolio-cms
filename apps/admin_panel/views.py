
# apps/admin_panel/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.files.storage import default_storage

from mongoengine.queryset.visitor import Q

from apps.common_utils import get_document_or_404, get_singleton_document, skill_sort_key

from apps.public.models import (
    Profile, Skill, Project, Blog,
    HomePage, AboutPage, ContactPage,
    Education, Interest, CoreValue,
    ResearchCategory, ResearchEntry,
    ContactSubmission, SkillCategory,
)
# ============================================
# DASHBOARD
# ============================================

# @login_required
# def dashboard(request):
#     """Admin dashboard"""
#     projects_count = Project.objects.count()
#     blogs_count = Blog.objects.count()
#     published_blogs = Blog.objects.filter(status='published').count()
#     draft_blogs = Blog.objects.filter(status='draft').count()
#     skills_count = Skill.objects.count()
    
#     # Recent projects
#     recent_projects = Project.objects.all().order_by('-created_at')[:5]
    
#     # Recent blogs
#     recent_blogs = Blog.objects.all().order_by('-created_at')[:5]
    
#     context = {
#         'projects_count': projects_count,
#         'blogs_count': blogs_count,
#         'published_blogs': published_blogs,
#         'draft_blogs': draft_blogs,
#         'skills_count': skills_count,
#         'recent_projects': recent_projects,
#         'recent_blogs': recent_blogs,
#     }
#     return render(request, 'admin/dashboard.html', context)
@login_required
def dashboard(request):
    """Admin dashboard"""
    projects_count = Project.objects.count()
    blogs_count = Blog.objects.count()
    published_blogs = Blog.objects.filter(status='published').count()
    draft_blogs = Blog.objects.filter(status='draft').count()
    skills_count = Skill.objects.count()
    
    # Contact submissions
    total_submissions = ContactSubmission.objects.count()
    unread_submissions = ContactSubmission.objects.filter(is_read=False).count()
    
    # Recent projects
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    
    # Recent blogs
    recent_blogs = Blog.objects.all().order_by('-created_at')[:5]
    
    # Recent contact submissions
    recent_submissions = ContactSubmission.objects.all().order_by('-submitted_at')[:5]
    
    context = {
        'projects_count': projects_count,
        'blogs_count': blogs_count,
        'published_blogs': published_blogs,
        'draft_blogs': draft_blogs,
        'skills_count': skills_count,
        'total_submissions': total_submissions,
        'unread_submissions': unread_submissions,
        'recent_projects': recent_projects,
        'recent_blogs': recent_blogs,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'admin/dashboard.html', context)

# ============================================
# BLOG MANAGEMENT
# ============================================

@login_required
def blogs_list(request):
    """List all blogs in admin"""
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        blogs = Blog.objects.filter(status=status_filter).order_by('-created_at')
    else:
        blogs = Blog.objects.all().order_by('-created_at')
    
    blogs_count = Blog.objects.count()
    published_blogs = Blog.objects.filter(status='published').count()
    draft_blogs = Blog.objects.filter(status='draft').count()
    
    context = {
        'blogs': blogs,
        'blogs_count': blogs_count,
        'published_blogs': published_blogs,
        'draft_blogs': draft_blogs,
    }
    return render(request, 'admin/blog_list.html', context)


@login_required
def blog_editor(request):
    """Create new blog"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        preview = request.POST.get('preview', '')
        tags_input = request.POST.get('tags', '')
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        status = request.POST.get('status', 'draft')
        read_time = request.POST.get('read_time', 5)
        cover_image = request.FILES.get('cover_image')
        is_active = request.POST.get('is_active') == 'on'
        
        # Determine status based on action button
        action = request.POST.get('action', 'draft')
        if action == 'publish':
            status = 'published'
        
        blog = Blog(
            title=title,
            content=content,
            preview=preview[:300],  # Limit to 300 chars
            tags=tags,
            status=status,
            read_time=read_time,
            is_active=is_active,
            published_date=timezone.now() if status == 'published' else None
        )
        if cover_image:
            blog.cover_image = cover_image
        blog.author = request.user
        blog.save()
        
        messages.success(request, f'Blog "{title}" created successfully!')
        return redirect('admin_blogs_list')
    
    return render(request, 'admin/blog_editor.html')


@login_required
def blog_edit(request, id):
    """Edit existing blog"""
    blog = get_document_or_404(Blog, id=id)
    
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.preview = request.POST.get('preview', '')[:300]
        
        tags_input = request.POST.get('tags', '')
        blog.tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        # Determine status based on action button
        action = request.POST.get('action', 'draft')
        if action == 'publish':
            blog.status = 'published'
            if not blog.published_date:
                blog.published_date = timezone.now()
        else:
            blog.status = request.POST.get('status', 'draft')
        
        blog.read_time = request.POST.get('read_time', 5)
        blog.is_active = request.POST.get('is_active') == 'on'
        
        if request.FILES.get('cover_image'):
            blog.cover_image = request.FILES.get('cover_image')
        
        blog.save()
        
        messages.success(request, f'Blog "{blog.title}" updated successfully!')
        return redirect('admin_blogs_list')
    
    context = {
        'blog': blog,
    }
    return render(request, 'admin/blog_editor.html', context)


@login_required
def blog_delete(request, id):
    """Delete blog"""
    blog = get_document_or_404(Blog, id=id)
    
    if request.method == 'POST':
        title = blog.title
        if blog.cover_image_path:
            default_storage.delete(blog.cover_image_path)
        blog.delete()
        messages.success(request, f'Blog "{title}" deleted successfully!')
        return redirect('admin_blogs_list')
    
    return redirect('admin_blogs_list')


# ============================================
# PROJECT MANAGEMENT
# ============================================

@login_required
def project_manager(request):
    """List all projects"""
    projects = Project.objects.all().order_by('-created_at')
    
    context = {
        'projects': projects,
    }
    return render(request, 'admin/project_manager.html', context)


@login_required
def project_form(request):
    """Create new project"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        tech_stack_input = request.POST.get('tech_stack', '')
        tech_stack = [tech.strip() for tech in tech_stack_input.split(',') if tech.strip()]
        
        image = request.FILES.get('image')
        github_link = request.POST.get('github_link', '')
        demo_link = request.POST.get('demo_link', '')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        project = Project(
            title=title,
            description=description,
            tech_stack=tech_stack,
            github_link=github_link,
            demo_link=demo_link,
            is_featured=is_featured,
            is_active=is_active
        )
        if image:
            project.image = image
        project.save()
        
        messages.success(request, f'Project "{title}" created successfully!')
        return redirect('admin_project_manager')
    
    return render(request, 'admin/project_form.html')


@login_required
def project_edit(request, id):
    """Edit existing project"""
    project = get_document_or_404(Project, id=id)
    
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        
        tech_stack_input = request.POST.get('tech_stack', '')
        project.tech_stack = [tech.strip() for tech in tech_stack_input.split(',') if tech.strip()]
        
        if request.FILES.get('image'):
            project.image = request.FILES.get('image')
        
        project.github_link = request.POST.get('github_link', '')
        project.demo_link = request.POST.get('demo_link', '')
        project.is_featured = request.POST.get('is_featured') == 'on'
        project.is_active = request.POST.get('is_active') == 'on'
        
        project.save()
        
        messages.success(request, f'Project "{project.title}" updated successfully!')
        return redirect('admin_project_manager')
    
    context = {
        'project': project,
    }
    return render(request, 'admin/project_form.html', context)


@login_required
def project_delete(request, id):
    """Delete project"""
    project = get_document_or_404(Project, id=id)
    
    if request.method == 'POST':
        title = project.title
        if project.image_path:
            default_storage.delete(project.image_path)
        project.delete()
        messages.success(request, f'Project "{title}" deleted successfully!')
        return redirect('admin_project_manager')
    
    return redirect('admin_project_manager')


# ============================================
# SKILLS MANAGEMENT
# ============================================

@login_required
def skills_manager(request):
    """List all skills"""
    skills = list(Skill.objects.all())
    skills.sort(key=skill_sort_key)
    categories = SkillCategory.objects.all()
    
    context = {
        'skills': skills,
        'categories': categories,
    }
    return render(request, 'admin/skills_manager.html', context)


@login_required
def skill_toggle_active(request, id):
    """Activate/deactivate a skill"""
    skill = get_document_or_404(Skill, id=id)
    target = not skill.is_active
    if target and skill.category and not skill.category.is_active:
        messages.warning(request, f'Skill "{skill.name}" cannot be activated because its category is inactive.')
        return redirect('admin_skills_manager')

    skill.is_active = target
    skill.save()
    status = 'activated' if skill.is_active else 'deactivated'
    messages.success(request, f'Skill "{skill.name}" {status}.')
    return redirect('admin_skills_manager')


@login_required
def skill_category_manage(request):
    """Create or update a skill category"""
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('admin_skills_manager')

        try:
            order = int(order)
        except (TypeError, ValueError):
            order = 0

        if category_id:
            category = get_document_or_404(SkillCategory, id=category_id)
            category.name = name
            category.description = description
            category.order = order
            category.is_active = is_active
            category.save()
            messages.success(request, f'Category "{name}" updated.')
        else:
            category = SkillCategory(
                name=name,
                description=description,
                order=order,
                is_active=is_active
            )
            category.save()
            messages.success(request, f'Category "{name}" added.')

    return redirect('admin_skills_manager')


@login_required
def skill_category_toggle_active(request, id):
    """Toggle category visibility"""
    category = get_document_or_404(SkillCategory, id=id)
    category.is_active = not category.is_active
    category.save()
    if not category.is_active:
        Skill.objects.filter(category=category).update(is_active=False)
    status = 'active' if category.is_active else 'inactive'
    messages.success(request, f'Category "{category.name}" is now {status}.')
    return redirect('admin_skills_manager')


@login_required
def skill_category_delete(request, id):
    """Delete skill category and clear relation"""
    category = get_document_or_404(SkillCategory, id=id)

    if request.method == 'POST':
        Skill.objects.filter(category=category).update(category=None)
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
    else:
        messages.error(request, 'Invalid request method for deleting category.')

    return redirect('admin_skills_manager')


@login_required
def skill_create(request):
    """Create new skill"""
    if request.method == 'POST':
        if request.POST.get('remove_resume'):
            if profile and profile.resume_path:
                default_storage.delete(profile.resume_path)
                profile.resume_path = None
                profile.save()
                messages.success(request, 'Resume removed successfully.')
            else:
                messages.warning(request, 'No resume to remove.')
            return redirect('admin_profile_manager')

        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        proficiency = request.POST.get('proficiency', 50)
        icon = request.POST.get('icon', '')
        is_active = request.POST.get('is_active') == 'on'
        category = SkillCategory.objects.filter(id=category_id).first() if category_id else None
        
        skill = Skill(
            name=name,
            category=category,
            is_active=is_active,
            proficiency=int(proficiency),
            icon=icon
        )
        skill.save()
        
        messages.success(request, f'Skill "{name}" added successfully!')
        return redirect('admin_skills_manager')
    
    return redirect('admin_skills_manager')


@login_required
def skill_edit(request, id):
    """Edit existing skill"""
    skill = get_document_or_404(Skill, id=id)
    
    if request.method == 'POST':
        skill.name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        skill.category = SkillCategory.objects.filter(id=category_id).first() if category_id else None
        skill.is_active = request.POST.get('is_active') == 'on'
        skill.proficiency = int(request.POST.get('proficiency', 50))
        skill.icon = request.POST.get('icon', '')
        
        skill.save()
        
        messages.success(request, f'Skill "{skill.name}" updated successfully!')
        return redirect('admin_skills_manager')
    
    return redirect('admin_skills_manager')


@login_required
def skill_delete(request, id):
    """Delete skill"""
    skill = get_document_or_404(Skill, id=id)
    
    if request.method == 'POST':
        name = skill.name
        skill.delete()
        messages.success(request, f'Skill "{name}" deleted successfully!')
        return redirect('admin_skills_manager')
    
    return redirect('admin_skills_manager')


# ============================================
# PROFILE MANAGEMENT
# ============================================

@login_required
def profile_manager(request):
    """Manage profile"""
    profile = Profile.objects.first()
    
    if request.method == 'POST':
        if request.POST.get('remove_resume'):
            if profile and profile.resume_path:
                default_storage.delete(profile.resume_path)
                profile.resume_path = None
                profile.save()
                messages.success(request, 'Resume removed successfully.')
            else:
                messages.warning(request, 'No resume to remove.')
            return redirect('admin_profile_manager')

        name = request.POST.get('name')
        role = request.POST.get('role')
        bio = request.POST.get('bio')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        github = request.POST.get('github', '')
        linkedin = request.POST.get('linkedin', '')
        twitter = request.POST.get('twitter', '')
        
        if profile:
            # Update existing profile
            profile.name = name
            profile.role = role
            profile.bio = bio
            profile.email = email
            profile.phone = phone
            profile.github = github
            profile.linkedin = linkedin
            profile.twitter = twitter
            
            if request.FILES.get('image'):
                if profile.image_path:
                    default_storage.delete(profile.image_path)
                profile.image = request.FILES.get('image')
            if request.FILES.get('resume'):
                if profile.resume_path:
                    default_storage.delete(profile.resume_path)
                profile.resume = request.FILES.get('resume')
            
            profile.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            # Create new profile
            profile = Profile(
                name=name,
                role=role,
                bio=bio,
                email=email,
                phone=phone,
                github=github,
                linkedin=linkedin,
                twitter=twitter,
            )
            if request.FILES.get('image'):
                profile.image = request.FILES.get('image')
            if request.FILES.get('resume'):
                profile.resume = request.FILES.get('resume')
            profile.save()
            messages.success(request, 'Profile created successfully!')
        
        return redirect('admin_profile_manager')
    
    context = {
        'profile': profile,
    }
    return render(request, 'admin/profile_manager.html', context)

@login_required
def home_page_manager(request):
    """Manage home page content"""
    home_page = get_singleton_document(
        HomePage,
        defaults={
            'hero_description': 'MCA Student specializing in Data Science, AI/ML, and Python Development.'
        }
    )
    
    if request.method == 'POST':
        home_page.hero_title = request.POST.get('hero_title')
        home_page.hero_subtitle = request.POST.get('hero_subtitle')
        home_page.hero_description = request.POST.get('hero_description')
        home_page.show_hero_title = request.POST.get('show_hero_title') == 'on'
        home_page.show_hero_subtitle = request.POST.get('show_hero_subtitle') == 'on'
        home_page.show_hero_description = request.POST.get('show_hero_description') == 'on'
        home_page.show_stats = request.POST.get('show_stats') == 'on'
        home_page.custom_stat_label = request.POST.get('custom_stat_label')
        home_page.custom_stat_value = request.POST.get('custom_stat_value')
        home_page.show_skills_summary = request.POST.get('show_skills_summary') == 'on'
        home_page.cta_title = request.POST.get('cta_title')
        home_page.cta_description = request.POST.get('cta_description')
        home_page.cta_button_text = request.POST.get('cta_button_text')
        home_page.show_cta_section = request.POST.get('show_cta_section') == 'on'
        
        home_page.save()
        messages.success(request, 'Home page content updated successfully!')
        return redirect('admin_home_page_manager')
    
    context = {
        'home_page': home_page,
    }
    return render(request, 'admin/home_page_manager.html', context)


# ============================================
# ABOUT PAGE MANAGEMENT
# ============================================

@login_required
def about_page_manager(request):
    """Manage about page content"""
    about_page = get_singleton_document(
        AboutPage,
        defaults={
            'introduction': '<p>Write your introduction here...</p>'
        }
    )
    
    if request.method == 'POST':
        about_page.page_title = request.POST.get('page_title')
        about_page.introduction = request.POST.get('introduction')
        about_page.show_education = request.POST.get('show_education') == 'on'
        about_page.interests_title = request.POST.get('interests_title')
        about_page.interests_subtitle = request.POST.get('interests_subtitle')
        about_page.values_title = request.POST.get('values_title')
        about_page.values_subtitle = request.POST.get('values_subtitle')
        about_page.show_page_title = request.POST.get('show_page_title') == 'on'
        about_page.show_introduction = request.POST.get('show_introduction') == 'on'
        about_page.show_stats_section = request.POST.get('show_stats_section') == 'on'
        about_page.show_interests = request.POST.get('show_interests') == 'on'
        about_page.show_values = request.POST.get('show_values') == 'on'
        
        about_page.save()
        messages.success(request, 'About page content updated successfully!')
        return redirect('admin_about_page_manager')
    
    # Get related data
    education_list = Education.objects.all()
    interests_list = Interest.objects.all()
    values_list = CoreValue.objects.all()
    research_categories = ResearchCategory.objects.all()
    research_entries_qs = ResearchEntry.objects.order_by('-created_at')
    research_category_filter = request.GET.get('research_category', '')
    research_search = request.GET.get('research_search', '').strip()
    if research_category_filter:
        category_obj = ResearchCategory.objects.filter(id=research_category_filter).first()
        if category_obj:
            research_entries_qs = research_entries_qs.filter(category=category_obj)
    if research_search:
        research_entries_qs = research_entries_qs.filter(
            Q(title__icontains=research_search) |
            Q(description__icontains=research_search) |
            Q(publication__icontains=research_search)
        )

    paginator = Paginator(research_entries_qs, 6)
    research_page_number = request.GET.get('research_page')
    research_entries_page = paginator.get_page(research_page_number)
    research_entries_total = research_entries_qs.count()
    
    context = {
        'about_page': about_page,
        'education_list': education_list,
        'interests_list': interests_list,
        'values_list': values_list,
        'research_categories': research_categories,
        'research_entries': research_entries_page,
        'research_entries_total': research_entries_total,
        'research_paginator': paginator,
        'research_page_obj': research_entries_page,
        'research_category_filter': research_category_filter,
        'research_search': research_search,
    }
    return render(request, 'admin/about_page_manager.html', context)


# Education CRUD
@login_required
def education_create(request):
    if request.method == 'POST':
        education = Education(
            degree=request.POST.get('degree'),
            institution=request.POST.get('institution'),
            year=request.POST.get('year'),
            description=request.POST.get('description'),
            order=request.POST.get('order', 0)
        )
        education.save()
        messages.success(request, 'Education entry added!')
        return redirect('admin_about_page_manager')
    return redirect('admin_about_page_manager')


@login_required
def education_edit(request, id):
    education = get_document_or_404(Education, id=id)
    if request.method == 'POST':
        education.degree = request.POST.get('degree')
        education.institution = request.POST.get('institution')
        education.year = request.POST.get('year')
        education.description = request.POST.get('description')
        education.order = request.POST.get('order', 0)
        education.save()
        messages.success(request, 'Education entry updated!')
        return redirect('admin_about_page_manager')
    return redirect('admin_about_page_manager')


@login_required
def education_delete(request, id):
    education = get_document_or_404(Education, id=id)
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education entry deleted!')
    return redirect('admin_about_page_manager')


@login_required
def education_toggle_active(request, id):
    education = get_document_or_404(Education, id=id)
    if request.method == 'POST':
        education.is_active = not education.is_active
        education.save()
        status = 'activated' if education.is_active else 'deactivated'
        messages.success(request, f'Education entry "{education.degree}" {status}.')
    else:
        messages.error(request, 'Invalid request method.')
    return redirect('admin_about_page_manager')


# Interest CRUD
@login_required
def interest_create(request):
    if request.method == 'POST':
        interest = Interest(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            icon=request.POST.get('icon'),
            color=request.POST.get('color', 'accent-primary'),
            order=request.POST.get('order', 0)
        )
        interest.save()
        messages.success(request, 'Interest added!')
        return redirect('admin_about_page_manager')
    return redirect('admin_about_page_manager')


@login_required
def interest_edit(request, id):
    interest = get_document_or_404(Interest, id=id)
    if request.method == 'POST':
        interest.title = request.POST.get('title')
        interest.description = request.POST.get('description')
        interest.icon = request.POST.get('icon')
        interest.color = request.POST.get('color', 'accent-primary')
        interest.order = request.POST.get('order', 0)
        interest.save()
        messages.success(request, 'Interest updated!')
        return redirect('admin_about_page_manager')
    return redirect('admin_about_page_manager')


@login_required
def interest_delete(request, id):
    interest = get_document_or_404(Interest, id=id)
    if request.method == 'POST':
        interest.delete()
        messages.success(request, 'Interest deleted!')
    return redirect('admin_about_page_manager')


@login_required
def interest_toggle_active(request, id):
    interest = get_document_or_404(Interest, id=id)
    if request.method == 'POST':
        interest.is_active = not interest.is_active
        interest.save()
        status = 'activated' if interest.is_active else 'deactivated'
        messages.success(request, f'Interest "{interest.title}" {status}.')
    else:
        messages.error(request, 'Invalid request method.')
    return redirect('admin_about_page_manager')


# Core Value CRUD
@login_required
def value_create(request):
    if request.method == 'POST':
        core_value = CoreValue(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            icon=request.POST.get('icon'),
            color=request.POST.get('color', 'accent-primary'),
            order=request.POST.get('order', 0)
        )
        core_value.save()
        messages.success(request, 'Core value added!')
        return redirect('admin_about_page_manager')
    return redirect('admin_about_page_manager')


@login_required
def value_edit(request, id):
    value = get_document_or_404(CoreValue, id=id)
    if request.method == 'POST':
        value.title = request.POST.get('title')
        value.description = request.POST.get('description')
        value.icon = request.POST.get('icon')
        value.color = request.POST.get('color', 'accent-primary')
        value.order = request.POST.get('order', 0)
        value.save()
        messages.success(request, 'Core value updated!')
        return redirect('admin_about_page_manager')
    return redirect('admin_about_page_manager')


@login_required
def value_delete(request, id):
    value = get_document_or_404(CoreValue, id=id)
    if request.method == 'POST':
        value.delete()
        messages.success(request, 'Core value deleted!')
    return redirect('admin_about_page_manager')


@login_required
def value_toggle_active(request, id):
    value = get_document_or_404(CoreValue, id=id)
    if request.method == 'POST':
        value.is_active = not value.is_active
        value.save()
        status = 'activated' if value.is_active else 'deactivated'
        messages.success(request, f'Core value "{value.title}" {status}.')
    else:
        messages.error(request, 'Invalid request method.')
    return redirect('admin_about_page_manager')


@login_required
def research_category_create(request):
    if request.method == 'POST':
        order = request.POST.get('order', 0)
        try:
            order = int(order)
        except (TypeError, ValueError):
            order = 0
        category = ResearchCategory(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            order=order,
            is_active=request.POST.get('is_active') == 'on'
        )
        category.save()
        messages.success(request, 'Research category added!')
    return redirect('admin_about_page_manager')


@login_required
def research_category_edit(request, id):
    category = get_document_or_404(ResearchCategory, id=id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        try:
            category.order = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            category.order = 0
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        messages.success(request, 'Research category updated!')
    return redirect('admin_about_page_manager')


@login_required
def research_category_delete(request, id):
    category = get_document_or_404(ResearchCategory, id=id)
    if request.method == 'POST':
        ResearchEntry.objects.filter(category=category).update(category=None)
        category.delete()
        messages.success(request, 'Research category deleted!')
    return redirect('admin_about_page_manager')


@login_required
def research_category_toggle_active(request, id):
    category = get_document_or_404(ResearchCategory, id=id)
    category.is_active = not category.is_active
    category.save()
    ResearchEntry.objects.filter(category=category).update(set__is_active=category.is_active)
    status = 'activated' if category.is_active else 'deactivated'
    messages.success(request, f'Research category \"{category.name}\" {status}.')
    return redirect('admin_about_page_manager')


@login_required
def research_entry_create(request):
    if request.method == 'POST':
        entry = ResearchEntry(
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            publication=request.POST.get('publication', ''),
            link=request.POST.get('link', ''),
            category=ResearchCategory.objects.filter(id=request.POST.get('category_id')).first()
        )
        entry.save()
        messages.success(request, 'Research entry added!')
    return redirect('admin_about_page_manager')


@login_required
def research_entry_edit(request, id):
    entry = get_document_or_404(ResearchEntry, id=id)
    if request.method == 'POST':
        entry.title = request.POST.get('title')
        entry.description = request.POST.get('description', '')
        entry.publication = request.POST.get('publication', '')
        entry.link = request.POST.get('link', '')
        entry.category = ResearchCategory.objects.filter(id=request.POST.get('category_id')).first()
        entry.save()
        messages.success(request, 'Research entry updated!')
    return redirect('admin_about_page_manager')


@login_required
def research_entry_toggle_active(request, id):
    entry = get_document_or_404(ResearchEntry, id=id)
    target = not entry.is_active
    if target and entry.category and not entry.category.is_active:
        messages.warning(request, f'Research entry \"{entry.title}\" cannot be activated while its category is inactive.')
        return redirect('admin_about_page_manager')
    entry.is_active = target
    entry.save()
    status = 'activated' if entry.is_active else 'deactivated'
    messages.success(request, f'Research entry \"{entry.title}\" {status}.')
    return redirect('admin_about_page_manager')

@login_required
def research_entry_delete(request, id):
    entry = get_document_or_404(ResearchEntry, id=id)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Research entry deleted!')
    return redirect('admin_about_page_manager')


# ============================================
# CONTACT PAGE MANAGEMENT
# ============================================

@login_required
def contact_page_manager(request):
    """Manage contact page content"""
    contact_page = get_singleton_document(
        ContactPage,
        defaults={
            'connect_description': '<p>Write your connect description here...</p>'
        }
    )
    
    if request.method == 'POST':
        contact_page.page_title = request.POST.get('page_title')
        contact_page.page_subtitle = request.POST.get('page_subtitle')
        contact_page.connect_title = request.POST.get('connect_title')
        contact_page.connect_description = request.POST.get('connect_description')
        contact_page.cta_title = request.POST.get('cta_title')
        contact_page.cta_description = request.POST.get('cta_description')
        contact_page.cta_button_text = request.POST.get('cta_button_text')
        contact_page.show_phone = request.POST.get('show_phone') == 'on'
        contact_page.show_location = request.POST.get('show_location') == 'on'
        contact_page.location_text = request.POST.get('location_text')
        contact_page.show_page_title = request.POST.get('show_page_title') == 'on'
        contact_page.show_page_subtitle = request.POST.get('show_page_subtitle') == 'on'
        contact_page.show_connect_section = request.POST.get('show_connect_section') == 'on'
        contact_page.show_contact_info = request.POST.get('show_contact_info') == 'on'
        contact_page.show_contact_form = request.POST.get('show_contact_form') == 'on'
        contact_page.show_cta_section = request.POST.get('show_cta_section') == 'on'
        
        contact_page.save()
        messages.success(request, 'Contact page content updated successfully!')
        return redirect('admin_contact_page_manager')
    
    context = {
        'contact_page': contact_page,
    }
    return render(request, 'admin/contact_page_manager.html', context)

@login_required
def contact_submissions(request):
    """View all contact form submissions"""
    # Filter options
    filter_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    submissions = ContactSubmission.objects.all()
    
    # Apply filters
    if filter_status == 'unread':
        submissions = submissions.filter(is_read=False)
    elif filter_status == 'read':
        submissions = submissions.filter(is_read=True)
    
    # Search
    if search_query:
        submissions = submissions.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(submissions, 10)  # 10 per page
    page_number = request.GET.get('page')
    submissions_page = paginator.get_page(page_number)
    
    # Stats
    total_submissions = ContactSubmission.objects.count()
    unread_count = ContactSubmission.objects.filter(is_read=False).count()
    read_count = ContactSubmission.objects.filter(is_read=True).count()
    
    context = {
        'submissions': submissions_page,
        'total_submissions': total_submissions,
        'unread_count': unread_count,
        'read_count': read_count,
        'filter_status': filter_status,
        'search_query': search_query,
    }
    return render(request, 'admin/contact_submissions.html', context)


@login_required
def contact_submission_detail(request, id):
    """View single contact submission"""
    submission = get_document_or_404(ContactSubmission, id=id)
    
    # Mark as read when viewed
    if not submission.is_read:
        submission.is_read = True
        submission.save()
    
    # Handle notes update
    if request.method == 'POST':
        submission.notes = request.POST.get('notes', '')
        submission.save()
        messages.success(request, 'Notes saved successfully!')
        return redirect('admin_contact_submission_detail', id=id)
    
    context = {
        'submission': submission,
    }
    return render(request, 'admin/contact_submission_detail.html', context)


@login_required
def contact_submission_delete(request, id):
    """Delete contact submission"""
    submission = get_document_or_404(ContactSubmission, id=id)
    
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'Contact submission deleted successfully!')
        return redirect('admin_contact_submissions')
    
    return redirect('admin_contact_submissions')


@login_required
def contact_submission_mark_read(request, id):
    """Toggle read status"""
    submission = get_document_or_404(ContactSubmission, id=id)
    submission.is_read = not submission.is_read
    submission.save()
    
    status = "read" if submission.is_read else "unread"
    messages.success(request, f'Message marked as {status}!')
    return redirect('admin_contact_submissions')


@login_required
def contact_submissions_bulk_action(request):
    """Handle bulk actions"""
    if request.method == 'POST':
        action = request.POST.get('action')
        submission_ids = request.POST.getlist('submission_ids')
        
        if not submission_ids:
            messages.error(request, 'No submissions selected!')
            return redirect('admin_contact_submissions')
        
        submissions = ContactSubmission.objects.filter(id__in=submission_ids)
        
        if action == 'mark_read':
            submissions.update(is_read=True)
            messages.success(request, f'{len(submission_ids)} messages marked as read!')
        elif action == 'mark_unread':
            submissions.update(is_read=False)
            messages.success(request, f'{len(submission_ids)} messages marked as unread!')
        elif action == 'delete':
            count = submissions.count()
            submissions.delete()
            messages.success(request, f'{count} messages deleted!')
        
        return redirect('admin_contact_submissions')
    
    return redirect('admin_contact_submissions')
