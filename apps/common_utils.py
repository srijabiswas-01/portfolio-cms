from django.http import Http404

from apps.public.models import SkillCategory


def get_document_or_404(document_class, **filters):
    """Fetch a MongoEngine document or raise Http404 the same way Django would."""

    try:
        return document_class.objects.get(**filters)
    except document_class.DoesNotExist:
        raise Http404(f"{document_class.__name__} not found.")


def get_active_skill_categories():
    """Return currently active skill categories as a list."""

    return list(SkillCategory.objects.filter(is_active=True))


def skill_sort_key(skill):
    """Sort skills by category name (case-insensitive) then proficiency desc."""

    category_name = skill.category_name or ""
    return (category_name.lower(), -skill.proficiency)


def get_singleton_document(document_class, defaults=None):
    """Return the unique singleton document or create it using defaults."""

    document = document_class.objects.first()
    if document:
        return document

    defaults = defaults or {}
    document = document_class(**defaults)
    document.save()
    return document
