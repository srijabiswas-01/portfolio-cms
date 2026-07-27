import hashlib
import html
import re
import threading
import time
from collections import Counter

from django.utils import timezone
from django.utils.html import strip_tags

from apps.public.models import (
    AboutPage,
    Achievement,
    Blog,
    Certification,
    CoreValue,
    Education,
    Experience,
    ExternalBlog,
    Interest,
    Profile,
    Project,
    ResearchEntry,
    ResumeFile,
    Skill,
)
from .models import KnowledgeDocument


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for", "from",
    "has", "have", "her", "how", "i", "in", "is", "it", "me", "my", "of", "on",
    "or", "srija", "tell", "that", "the", "to", "what", "which", "with", "you", "your",
}
SYNC_LOCK = threading.Lock()
LAST_SYNC = 0.0


def clean_text(value):
    value = html.unescape(strip_tags(str(value or "")))
    return re.sub(r"\s+", " ", value).strip()


def _parts(*values):
    return " | ".join(part for part in (clean_text(value) for value in values) if part)


def _chunks(text, size=1200, overlap=160):
    text = clean_text(text)
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start + size // 2:
                end = boundary
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def _add(items, source_type, source_id, title, text, url, chunk=True):
    source_id = str(source_id or "singleton")
    content_chunks = _chunks(text) if chunk else [clean_text(text)]
    for index, content in enumerate(filter(None, content_chunks)):
        items.append({
            "source_key": f"{source_type}:{source_id}:{index}",
            "source_type": source_type,
            "source_id": source_id,
            "title": clean_text(title),
            "text": content,
            "url": url,
        })


def collect_public_knowledge():
    items = []
    profile = Profile.objects.first()
    if profile:
        _add(items, "profile", profile.id, profile.name, _parts(
            f"Name: {profile.name}", f"Role: {profile.role}", profile.bio,
            f"Email: {profile.email}", f"Phone: {profile.phone}",
            f"GitHub: {profile.github}", f"LinkedIn: {profile.linkedin}",
        ), "/about/")

    about = AboutPage.objects.first()
    if about and about.introduction:
        _add(items, "about", about.id, about.page_title, about.introduction, "/about/")

    for skill in Skill.objects.filter(is_active=True):
        if skill.category and not skill.category.is_active:
            continue
        _add(items, "skill", skill.id, skill.name, _parts(
            f"Skill: {skill.name}", f"Category: {skill.category_name}",
            f"Proficiency: {skill.proficiency_percent}%",
        ), "/skills/", chunk=False)

    for project in Project.objects.filter(is_active=True):
        _add(items, "project", project.id, project.title, _parts(
            f"Project: {project.title}", project.description,
            f"Technology stack: {', '.join(project.tech_stack)}",
            f"GitHub: {project.github_link}", f"Demo: {project.demo_link}",
        ), f"/projects/{project.id}/")

    for certificate in Certification.objects.filter(is_active=True):
        _add(items, "certification", certificate.id, certificate.name, _parts(
            f"Certification: {certificate.name}", certificate.details,
            f"Start: {certificate.start_month}", f"End: {certificate.end_month or 'No expiry'}",
            f"Credential: {certificate.credential_url}",
        ), "/certifications/", chunk=False)

    for education in Education.objects.filter(is_active=True):
        _add(items, "education", education.id, education.degree, _parts(
            education.degree, education.institution, education.year, education.description,
            f"{education.grade_format}: {education.grade}" if education.grade else "",
            education.link,
        ), "/about/", chunk=False)

    for experience in Experience.objects.filter(is_active=True):
        _add(items, "experience", experience.id, experience.title, _parts(
            experience.title, experience.organization, experience.period, experience.description,
        ), "/about/")

    for achievement in Achievement.objects.filter(is_active=True):
        _add(items, "achievement", achievement.id, achievement.title, _parts(
            achievement.title, achievement.year, achievement.description, achievement.link,
        ), achievement.link or "/about/", chunk=False)

    for research in ResearchEntry.objects.filter(is_active=True):
        if research.category and not research.category.is_active:
            continue
        _add(items, "research", research.id, research.title, _parts(
            research.title, research.description, research.publication,
            f"Category: {research.category.name if research.category else ''}", research.link,
        ), research.link or "/about/")

    for interest in Interest.objects.filter(is_active=True):
        _add(items, "interest", interest.id, interest.title, _parts(interest.title, interest.description), "/about/", chunk=False)
    for value in CoreValue.objects.filter(is_active=True):
        _add(items, "value", value.id, value.title, _parts(value.title, value.description), "/about/", chunk=False)

    for blog in Blog.objects.filter(status="published", is_active=True):
        if blog.category and not blog.category.is_active:
            continue
        _add(items, "blog", blog.id, blog.title, _parts(
            blog.title, blog.preview, blog.content,
            f"Category: {blog.category_name}", f"Tags: {', '.join(blog.tags)}",
        ), f"/blog/{blog.id}/")

    for article in ExternalBlog.objects.filter(is_active=True):
        if article.category and not article.category.is_active:
            continue
        _add(items, "external_blog", article.id, article.title, _parts(
            article.title, article.preview, f"Platform: {article.platform}",
            f"Category: {article.category_name}",
        ), article.url, chunk=False)

    resume = ResumeFile.objects.filter(is_active=True).first()
    if resume:
        _add(items, "resume", resume.id, "Resume", "Srija's current resume is available to view and download.", "/resume/", chunk=False)
    return items


def sync_knowledge(force=False):
    global LAST_SYNC
    if not force and LAST_SYNC and time.monotonic() - LAST_SYNC < 300:
        return KnowledgeDocument.objects(is_active=True).count()
    with SYNC_LOCK:
        if not force and LAST_SYNC and time.monotonic() - LAST_SYNC < 300:
            return KnowledgeDocument.objects(is_active=True).count()
        items = collect_public_knowledge()
        active_keys = set()
        now = timezone.now()
        for item in items:
            active_keys.add(item["source_key"])
            digest = hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
            document = KnowledgeDocument.objects(source_key=item["source_key"]).first()
            if not document:
                document = KnowledgeDocument(source_key=item["source_key"])
            if document.content_hash != digest or not document.is_active:
                for key, value in item.items():
                    setattr(document, key, value)
                document.content_hash = digest
                document.is_active = True
                document.updated_at = now
                document.save()
        if active_keys:
            KnowledgeDocument.objects(source_key__nin=list(active_keys)).update(set__is_active=False)
        else:
            KnowledgeDocument.objects.update(set__is_active=False)
        LAST_SYNC = time.monotonic()
        return len(active_keys)


def _tokens(text):
    tokens = []
    for token in re.findall(r"[a-z0-9+#.]{2,}", clean_text(text).lower()):
        if token in STOP_WORDS:
            continue
        if token.endswith("s") and len(token) > 4 and not token.endswith("ss"):
            token = token[:-1]
        tokens.append(token)
    return tokens


def retrieve(question, limit=5):
    sync_knowledge()
    lowered = clean_text(question).lower()
    query_tokens = _tokens(question)
    intent_types = set()
    if any(phrase in lowered for phrase in ("about srija", "who is srija", "introduce", "yourself")):
        intent_types.update(("profile", "about"))
        query_tokens.append("profile")
    if any(word in lowered for word in ("skill", "technology", "technologies", "expertise", "language")):
        intent_types.add("skill")
        query_tokens.append("skill")
    if any(word in lowered for word in ("project", "portfolio", "application")):
        intent_types.add("project")
    if any(word in lowered for word in ("contact", "hire", "email", "phone", "linkedin")):
        intent_types.add("profile")
    if "resume" in lowered or "cv" in lowered:
        intent_types.add("resume")
    if any(word in lowered for word in ("certificate", "certification", "credential")):
        intent_types.add("certification")
    if any(word in lowered for word in ("experience", "work")):
        intent_types.add("experience")
    if any(word in lowered for word in ("education", "degree", "college", "university")):
        intent_types.add("education")
    if any(word in lowered for word in ("blog", "article", "post")):
        intent_types.update(("blog", "external_blog"))
    if not query_tokens and not intent_types:
        return []
    query_counts = Counter(query_tokens)
    results = []
    for document in KnowledgeDocument.objects.filter(is_active=True):
        title_tokens = Counter(_tokens(document.title))
        text_tokens = Counter(_tokens(document.text))
        title_score = sum(min(count, title_tokens[token]) for token, count in query_counts.items()) * 5
        text_score = sum(min(count, text_tokens[token]) for token, count in query_counts.items())
        phrase_bonus = 4 if clean_text(question).lower() in document.text.lower() else 0
        intent_bonus = 7 if document.source_type in intent_types else 0
        if any(word in lowered for word in ("contact", "hire", "email", "phone", "linkedin")) and document.source_type == "profile":
            intent_bonus += 8
        if "resume" in lowered and document.source_type == "resume":
            intent_bonus += 8
        score = title_score + text_score + phrase_bonus + intent_bonus
        if score > 0:
            results.append((score, document))
    results.sort(key=lambda item: (item[0], item[1].updated_at), reverse=True)
    return [document for _, document in results[:limit]]
