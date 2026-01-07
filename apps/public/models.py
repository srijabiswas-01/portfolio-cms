import os
from types import SimpleNamespace

from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import slugify

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)
from mongoengine import NULLIFY


def _now():
    return timezone.now()


class StoredFileProxy:
    """A tiny stand-in for Django's FieldFile so templates can keep using `.url` and `.name`."""

    def __init__(self, path):
        self._path = path

    def __bool__(self):
        return bool(self._path)

    @property
    def url(self):
        if not self._path:
            return ""
        return default_storage.url(self._path)

    @property
    def name(self):
        return self._path or ""

    def __str__(self):
        return self.url


class FileFieldDescriptor:
    """Descriptor that persists UploadedFile via Django's storage and keeps the original path."""

    def __init__(self, storage_field, upload_to):
        self.storage_field = storage_field
        self.upload_to = upload_to

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return StoredFileProxy(getattr(instance, self.storage_field))

    def __set__(self, instance, value):
        if not value:
            setattr(instance, self.storage_field, None)
            return

        if hasattr(value, "read") and hasattr(value, "name"):
            destination = os.path.join(self.upload_to, value.name)
            saved_path = default_storage.save(destination, value)
            if os.sep != "/":
                saved_path = saved_path.replace(os.sep, "/")
            setattr(instance, self.storage_field, saved_path)
            return

        setattr(instance, self.storage_field, value)


class TimestampedDocument(Document):
    meta = {"abstract": True}

    created_at = DateTimeField(default=_now)
    updated_at = DateTimeField(default=_now)

    def save(self, *args, **kwargs):
        now = _now()
        if not self.created_at:
            self.created_at = now
        self.updated_at = now
        return super().save(*args, **kwargs)

    @property
    def id_str(self):
        return str(self.id)


class UpdatedDocument(Document):
    meta = {"abstract": True}

    updated_at = DateTimeField(default=_now)

    def save(self, *args, **kwargs):
        self.updated_at = _now()
        return super().save(*args, **kwargs)


class SingletonDocument(UpdatedDocument):
    meta = {"abstract": True}

    def save(self, *args, **kwargs):
        if not self.id and self.__class__.objects.count() > 0:
            raise ValueError(f"Only one {self.__class__.__name__} instance is allowed")
        return super().save(*args, **kwargs)


class TestPost(Document):
    title = StringField(required=True)
    content = StringField()

    meta = {"collection": "test_posts"}


class SkillCategory(Document):
    name = StringField(max_length=100, required=True, unique=True)
    slug = StringField(max_length=120, unique=True)
    description = StringField(max_length=255, default="")
    is_active = BooleanField(default=True)
    order = IntField(default=0)

    meta = {"collection": "skill_categories", "ordering": ["-order", "name"]}

    def __str__(self):
        return self.name

    @property
    def id_str(self):
        return str(self.id)

    @property
    def proficiency_percent(self):
        value_raw = str(self.proficiency or '').strip()
        if value_raw.endswith('%'):
            value_raw = value_raw[:-1]
        try:
            value = int(''.join(ch for ch in value_raw if ch.isdigit()))
        except (TypeError, ValueError):
            value = 0
        return max(0, min(100, value))

    def save(self, *args, **kwargs):
        self.slug = self._generate_slug() if not self.slug else self.slug
        return super().save(*args, **kwargs)

    def _generate_slug(self):
        base = slugify(self.name) or "category"
        candidate = base
        counter = 1

        while True:
            query = SkillCategory.objects(slug=candidate)
            if self.id:
                query = query.filter(id__ne=self.id)
            if query.count() == 0:
                break
            candidate = f"{base}-{counter}"
            counter += 1

        return candidate


class Profile(TimestampedDocument):
    name = StringField(max_length=100, required=True)
    role = StringField(max_length=100, required=True)
    bio = StringField()
    email = StringField(required=True)
    phone = StringField()
    github = StringField()
    linkedin = StringField()
    twitter = StringField()
    image_path = StringField()
    resume_path = StringField()

    image = FileFieldDescriptor("image_path", "profiles")
    resume = FileFieldDescriptor("resume_path", "resumes")

    meta = {"collection": "profile"}

    def __str__(self):
        return self.name


class Skill(TimestampedDocument):
    name = StringField(max_length=100, required=True)
    category = ReferenceField("SkillCategory", reverse_delete_rule=NULLIFY)
    is_active = BooleanField(default=True)
    proficiency = IntField(default=0)
    icon = StringField(max_length=50, default="")

    meta = {"collection": "skills", "ordering": ["-proficiency"]}

    def __str__(self):
        return self.name

    @property
    def category_name(self):
        return self.category.name if self.category else "Uncategorized"

    @property
    def proficiency_percent(self):
        value = self.proficiency
        if value is None:
            value = 0
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 0
        return max(0, min(100, value))


class Project(TimestampedDocument):
    title = StringField(max_length=200, required=True)
    description = StringField()
    tech_stack = ListField(StringField(), default=list)
    image_path = StringField()
    github_link = StringField()
    demo_link = StringField()
    is_featured = BooleanField(default=False)
    is_active = BooleanField(default=True)

    image = FileFieldDescriptor("image_path", "projects")

    meta = {"collection": "projects", "ordering": ["-created_at"]}

    def __str__(self):
        return self.title


class Blog(TimestampedDocument):
    STATUS_CHOICES = ("draft", "published")

    title = StringField(max_length=200, required=True)
    content = StringField()
    preview = StringField(max_length=300)
    cover_image_path = StringField()
    tags = ListField(StringField(), default=list)
    status = StringField(choices=STATUS_CHOICES, default="draft")
    is_active = BooleanField(default=True)
    read_time = IntField(default=5)
    author_username = StringField()
    author_display_name = StringField()
    author_id = StringField()
    published_date = DateTimeField()

    cover_image = FileFieldDescriptor("cover_image_path", "blogs")

    meta = {"collection": "blogs", "ordering": ["-created_at"]}

    def __str__(self):
        return self.title

    @property
    def author(self):
        if not self.author_username:
            return None
        return SimpleNamespace(
            username=self.author_username,
            get_full_name=lambda: self.author_display_name or self.author_username,
        )

    @author.setter
    def author(self, user):
        if not user:
            self.author_username = None
            self.author_display_name = None
            self.author_id = None
            return

        self.author_username = getattr(user, "username", "")
        self.author_display_name = (
            getattr(user, "get_full_name", lambda: "")() or self.author_username
        )
        self.author_id = str(getattr(user, "pk", getattr(user, "id", "")))


class HomePage(SingletonDocument):
    hero_title = StringField(max_length=200, default="Your Name")
    hero_subtitle = StringField(default="MCA Student | Data Scientist")
    hero_description = StringField(default="")
    show_hero_title = BooleanField(default=True)
    show_hero_subtitle = BooleanField(default=True)
    show_hero_description = BooleanField(default=True)
    show_stats = BooleanField(default=True)
    custom_stat_label = StringField(max_length=50, default="Tech Stack")
    custom_stat_value = StringField(max_length=20, default="5+")
    cta_title = StringField(max_length=200, default="Let's Work Together")
    cta_description = StringField(default="Have a project in mind? Let's create something amazing together.")
    cta_button_text = StringField(max_length=50, default="Get In Touch")
    show_cta_section = BooleanField(default=True)
    show_skills_summary = BooleanField(default=True)

    meta = {
        "collection": "home_page",
        "verbose_name": "Home Page Content",
        "verbose_name_plural": "Home Page Content",
    }

    def __str__(self):
        return "Home Page Content"


class AboutPage(SingletonDocument):
    page_title = StringField(max_length=200, default="About Me")
    introduction = StringField(default="")
    show_page_title = BooleanField(default=True)
    show_introduction = BooleanField(default=True)
    show_stats_section = BooleanField(default=True)
    show_interests = BooleanField(default=True)
    show_values = BooleanField(default=True)
    show_experiences_section = BooleanField(default=True)
    show_achievements_section = BooleanField(default=True)
    show_education = BooleanField(default=True)
    interests_title = StringField(max_length=200, default="Interests & Passion")
    interests_subtitle = StringField(max_length=200, default="What drives me")
    values_title = StringField(max_length=200, default="Core Values")
    values_subtitle = StringField(max_length=200, default="Principles I live by")
    experiences_title = StringField(max_length=200, default="Experiences")
    experiences_description = StringField(default="")
    achievements_title = StringField(max_length=200, default="Achievements")
    achievements_description = StringField(default="")

    meta = {
        "collection": "about_page",
        "verbose_name": "About Page Content",
        "verbose_name_plural": "About Page Content",
    }

    def __str__(self):
        return "About Page Content"


class Education(TimestampedDocument):
    degree = StringField(max_length=200, required=True)
    institution = StringField(max_length=200, required=True)
    year = StringField(max_length=50)
    description = StringField()
    order = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "education", "ordering": ["order", "-created_at"]}

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(TimestampedDocument):
    title = StringField(max_length=200, required=True)
    organization = StringField(max_length=200, default="")
    period = StringField(max_length=100, default="")
    description = StringField()
    order = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "experiences", "ordering": ["order", "-created_at"]}

    def __str__(self):
        org = f" at {self.organization}" if self.organization else ""
        return f"{self.title}{org}"


class Achievement(TimestampedDocument):
    title = StringField(max_length=200, required=True)
    description = StringField()
    year = StringField(max_length=50, default="")
    link = StringField(default="")
    order = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "achievements", "ordering": ["order", "-created_at"]}

    def __str__(self):
        return self.title


class Interest(TimestampedDocument):
    title = StringField(max_length=100, required=True)
    description = StringField(max_length=200)
    icon = StringField(max_length=50)
    color = StringField(max_length=20, default="accent-primary")
    order = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "interests", "ordering": ["order"]}

    def __str__(self):
        return self.title


class CoreValue(TimestampedDocument):
    title = StringField(max_length=100, required=True)
    description = StringField()
    icon = StringField(max_length=50)
    color = StringField(max_length=20, default="accent-primary")
    order = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "core_values", "ordering": ["order"]}

    def __str__(self):
        return self.title


class ResearchCategory(TimestampedDocument):
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=255, default="")
    order = IntField(default=0)
    is_active = BooleanField(default=True)

    meta = {"collection": "research_categories", "ordering": ["order", "-created_at"]}

    def __str__(self):
        return self.name


class ResearchEntry(TimestampedDocument):
    title = StringField(max_length=200, required=True)
    description = StringField()
    publication = StringField(max_length=200, default="")
    link = StringField(default="")
    category = ReferenceField(ResearchCategory, reverse_delete_rule=NULLIFY)
    is_active = BooleanField(default=True)

    meta = {"collection": "research_entries", "ordering": ["-created_at"]}

    def __str__(self):
        return self.title


class ContactPage(SingletonDocument):
    page_title = StringField(max_length=200, default="Get In Touch")
    page_subtitle = StringField(default="Have a project in mind or want to collaborate? I'd love to hear from you!")
    show_page_title = BooleanField(default=True)
    show_page_subtitle = BooleanField(default=True)
    connect_title = StringField(max_length=200, default="Let's Connect")
    connect_description = StringField(default="Share your ideas and we will turn them into reality.")
    show_connect_section = BooleanField(default=True)
    cta_title = StringField(max_length=200, default="Ready to Start a Project?")
    cta_description = StringField(default="Let's work together to bring your ideas to life.")
    cta_button_text = StringField(max_length=50, default="View My Work")
    show_cta_section = BooleanField(default=True)
    show_contact_info = BooleanField(default=True)
    show_contact_form = BooleanField(default=True)
    show_phone = BooleanField(default=True)
    show_location = BooleanField(default=True)
    location_text = StringField(max_length=200, default="India")

    meta = {
        "collection": "contact_page",
        "verbose_name": "Contact Page Content",
        "verbose_name_plural": "Contact Page Content",
    }

    def __str__(self):
        return "Contact Page Content"


class ContactSubmission(Document):
    name = StringField(max_length=200, required=True)
    email = StringField(required=True)
    subject = StringField(max_length=300)
    message = StringField()
    submitted_at = DateTimeField(default=_now)
    is_read = BooleanField(default=False)
    notes = StringField(default="")

    meta = {"collection": "contact_submissions", "ordering": ["-submitted_at"]}

    def __str__(self):
        return f"{self.name} - {self.subject}"
