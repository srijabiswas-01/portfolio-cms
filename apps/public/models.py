# from django.db import models
# from django.contrib.auth.models import User

# class Profile(models.Model):
#     name = models.CharField(max_length=100)
#     role = models.CharField(max_length=100)
#     bio = models.TextField()
#     email = models.EmailField()
#     phone = models.CharField(max_length=20, blank=True)
#     image = models.ImageField(upload_to='profiles/', blank=True, null=True)
#     resume = models.FileField(upload_to='resumes/', blank=True, null=True)
#     github = models.URLField(blank=True)
#     linkedin = models.URLField(blank=True)
#     twitter = models.URLField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'profile'
    
#     def __str__(self):
#         return self.name

# class Skill(models.Model):
#     CATEGORY_CHOICES = [
#         ('programming', 'Programming'),
#         ('data_science', 'Data Science'),
#         ('web', 'Web Development'),
#         ('tools', 'Tools & Technologies'),
#         ('other', 'Other'),
#     ]
    
#     name = models.CharField(max_length=100)
#     category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
#     proficiency = models.IntegerField(default=0)  # 0-100
#     icon = models.CharField(max_length=50, blank=True)  # Bootstrap icon name
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         db_table = 'skills'
#         ordering = ['-proficiency', 'name']
    
#     def __str__(self):
#         return self.name

# class Project(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     tech_stack = models.JSONField(default=list)  # List of technologies
#     image = models.ImageField(upload_to='projects/', blank=True, null=True)
#     github_link = models.URLField(blank=True)
#     demo_link = models.URLField(blank=True)
#     is_featured = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'projects'
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return self.title

# class Blog(models.Model):
#     STATUS_CHOICES = [
#         ('draft', 'Draft'),
#         ('published', 'Published'),
#     ]
    
#     title = models.CharField(max_length=200)
#     content = models.TextField()  # HTML from QuillJS
#     preview = models.TextField(max_length=300)
#     cover_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
#     tags = models.JSONField(default=list)  # List of tags
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
#     read_time = models.IntegerField(default=5)  # Minutes
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     published_date = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'blogs'
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return self.title

# apps/public/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from mongoengine import Document, StringField

class TestPost(Document):
    title = StringField(required=True)
    content = StringField()

    meta = {
        'collection': 'test_posts'
    }
class SkillCategory(models.Model):
    """Admin-managed skill categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'skill_categories'
        ordering = ['-order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'category'
            slug = base_slug
            counter = 1
            while SkillCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Profile(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profile'
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='skills'
    )
    is_active = models.BooleanField(default=True)
    proficiency = models.IntegerField(default=0)  # 0-100
    icon = models.CharField(max_length=50, blank=True)  # Bootstrap icon name
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'skills'
        ordering = ['category__name', '-proficiency']
    
    def __str__(self):
        return self.name

    @property
    def category_name(self):
        return self.category.name if self.category else 'Uncategorized'


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.JSONField(default=list)  # List of technologies
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    github_link = models.URLField(blank=True)
    demo_link = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()  # HTML from QuillJS
    preview = models.TextField(max_length=300)
    cover_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    tags = models.JSONField(default=list)  # List of tags
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    read_time = models.IntegerField(default=5)  # Minutes
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blogs'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


# NEW MODELS FOR PAGE CONTENT MANAGEMENT

class HomePage(models.Model):
    """Home page content management"""
    hero_title = models.CharField(max_length=200, default="Your Name")
    hero_subtitle = models.TextField(default="MCA Student | Data Scientist")
    hero_description = models.TextField()
    show_hero_title = models.BooleanField(default=True)
    show_hero_subtitle = models.BooleanField(default=True)
    show_hero_description = models.BooleanField(default=True)
    
    # Statistics
    show_stats = models.BooleanField(default=True)
    custom_stat_label = models.CharField(max_length=50, default="Tech Stack")
    custom_stat_value = models.CharField(max_length=20, default="5+")
    
    # CTA Section
    cta_title = models.CharField(max_length=200, default="Let's Work Together")
    cta_description = models.TextField(default="Have a project in mind? Let's create something amazing together.")
    cta_button_text = models.CharField(max_length=50, default="Get In Touch")
    show_cta_section = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'home_page'
        verbose_name = 'Home Page Content'
        verbose_name_plural = 'Home Page Content'
    
    def __str__(self):
        return "Home Page Content"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and HomePage.objects.exists():
            raise ValueError('Only one HomePage instance is allowed')
        return super().save(*args, **kwargs)


class AboutPage(models.Model):
    """About page content management"""
    page_title = models.CharField(max_length=200, default="About Me")
    introduction = models.TextField()  # HTML from QuillJS
    show_page_title = models.BooleanField(default=True)
    show_introduction = models.BooleanField(default=True)
    show_stats_section = models.BooleanField(default=True)
    show_interests = models.BooleanField(default=True)
    show_values = models.BooleanField(default=True)
    
    # Education
    
    show_education = models.BooleanField(default=True)
    # Interests Section
    interests_title = models.CharField(max_length=200, default="Interests & Passion")
    interests_subtitle = models.CharField(max_length=200, default="What drives me")
    
    # Values Section
    values_title = models.CharField(max_length=200, default="Core Values")
    values_subtitle = models.CharField(max_length=200, default="Principles I live by")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'about_page'
        verbose_name = 'About Page Content'
        verbose_name_plural = 'About Page Content'
    
    def __str__(self):
        return "About Page Content"
    
    def save(self, *args, **kwargs):
        if not self.pk and AboutPage.objects.exists():
            raise ValueError('Only one AboutPage instance is allowed')
        return super().save(*args, **kwargs)


class Education(models.Model):
    """Education entries for About page"""
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.CharField(max_length=50)
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'education'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Interest(models.Model):
    """Interests for About page"""
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=50)  # Bootstrap icon
    color = models.CharField(max_length=20, default='accent-primary')  # CSS color class
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'interests'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class CoreValue(models.Model):
    """Core values for About page"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Bootstrap icon
    color = models.CharField(max_length=20, default='accent-primary')
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'core_values'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class ContactPage(models.Model):
    """Contact page content management"""
    page_title = models.CharField(max_length=200, default="Get In Touch")
    page_subtitle = models.TextField(default="Have a project in mind or want to collaborate? I'd love to hear from you!")
    show_page_title = models.BooleanField(default=True)
    show_page_subtitle = models.BooleanField(default=True)
    
    # Connect Section
    connect_title = models.CharField(max_length=200, default="Let's Connect")
    connect_description = models.TextField()  # HTML from QuillJS
    show_connect_section = models.BooleanField(default=True)
    
    # CTA Section
    cta_title = models.CharField(max_length=200, default="Ready to Start a Project?")
    cta_description = models.TextField(default="Let's work together to bring your ideas to life.")
    cta_button_text = models.CharField(max_length=50, default="View My Work")
    show_cta_section = models.BooleanField(default=True)
    
    # Display toggles
    show_contact_info = models.BooleanField(default=True)
    show_contact_form = models.BooleanField(default=True)
    
    # Contact Info
    show_phone = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    location_text = models.CharField(max_length=200, default="India")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contact_page'
        verbose_name = 'Contact Page Content'
        verbose_name_plural = 'Contact Page Content'
    
    def __str__(self):
        return "Contact Page Content"
    
    def save(self, *args, **kwargs):
        if not self.pk and ContactPage.objects.exists():
            raise ValueError('Only one ContactPage instance is allowed')
        return super().save(*args, **kwargs)
# Add to apps/public/models.py

class ContactSubmission(models.Model):
    """Store contact form submissions"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="Admin notes about this submission")
    
    class Meta:
        db_table = 'contact_submissions'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
