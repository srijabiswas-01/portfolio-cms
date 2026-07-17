from django.utils import timezone
from mongoengine import BooleanField, DateTimeField, DictField, Document, ListField, StringField


class KnowledgeDocument(Document):
    source_key = StringField(required=True, unique=True)
    source_type = StringField(required=True)
    source_id = StringField(default="")
    title = StringField(required=True)
    text = StringField(required=True)
    url = StringField(default="")
    content_hash = StringField(required=True)
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=timezone.now)

    meta = {
        "collection": "assistant_knowledge",
        "indexes": ["source_type", "is_active", "updated_at"],
    }


class ChatMessage(Document):
    session_id = StringField(required=True)
    role = StringField(required=True, choices=("user", "assistant"))
    content = StringField(required=True)
    sources = ListField(DictField(), default=list)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        "collection": "assistant_messages",
        "ordering": ["created_at"],
        "indexes": ["session_id", "created_at"],
    }
