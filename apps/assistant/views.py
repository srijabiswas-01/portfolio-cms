import json
import re
import threading
import time
from collections import defaultdict, deque
from datetime import timedelta

from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .knowledge import retrieve
from .llm import AssistantProviderError, generate_answer
from .models import ChatMessage


SESSION_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{16,64}$")
RATE_WINDOWS = defaultdict(deque)
RATE_LOCK = threading.Lock()
LAST_HISTORY_CLEANUP = 0.0


def _conversational_reply(question):
    """Handle simple conversation without requiring a portfolio search or AI call."""
    normalized = re.sub(r"[^a-z0-9\s']", " ", question.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if re.fullmatch(r"(thank you|thanks|thank you so much|thanks a lot|thx)", normalized):
        return "You're welcome! Feel free to ask me anything else about Srija's skills, projects, experience, certifications, or contact details."
    if re.fullmatch(r"(hi|hello|hey|hi there|hello there|good morning|good afternoon|good evening)", normalized):
        return "Hello! I'm Srija's portfolio assistant. What would you like to know about her work, skills, experience, or projects?"
    if re.fullmatch(r"(bye|goodbye|see you|see you later)", normalized):
        return "Goodbye! Thanks for visiting Srija's portfolio."
    if re.fullmatch(r"(how are you|how are you doing)", normalized):
        return "I'm doing well and ready to help you explore Srija's portfolio. What would you like to know?"
    return None


def _client_key(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "unknown"))[:80]


def _rate_limited(key, maximum=12, window=60):
    now = time.monotonic()
    with RATE_LOCK:
        timestamps = RATE_WINDOWS[key]
        while timestamps and timestamps[0] <= now - window:
            timestamps.popleft()
        if len(timestamps) >= maximum:
            return True
        timestamps.append(now)
        return False


def _enabled():
    return settings.AI_ASSISTANT_ENABLED


def _cleanup_old_history():
    global LAST_HISTORY_CLEANUP
    now = time.monotonic()
    if LAST_HISTORY_CLEANUP and now - LAST_HISTORY_CLEANUP < 86400:
        return
    ChatMessage.objects(created_at__lt=timezone.now() - timedelta(days=30)).delete()
    LAST_HISTORY_CLEANUP = now


@require_POST
@csrf_protect
def chat(request):
    if not _enabled():
        return JsonResponse({"error": "The portfolio assistant is currently unavailable."}, status=503)
    _cleanup_old_history()
    try:
        if int(request.META.get("CONTENT_LENGTH") or 0) > 12000:
            return JsonResponse({"error": "Request is too large."}, status=413)
    except ValueError:
        return JsonResponse({"error": "Invalid request size."}, status=400)
    if _rate_limited(_client_key(request)):
        return JsonResponse({"error": "Too many questions. Please wait a minute and try again."}, status=429)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)

    question = str(payload.get("question", "")).strip()
    session_id = str(payload.get("session_id", "")).strip()
    if not 2 <= len(question) <= 500:
        return JsonResponse({"error": "Please enter a question between 2 and 500 characters."}, status=400)
    if not SESSION_PATTERN.fullmatch(session_id):
        return JsonResponse({"error": "Invalid chat session."}, status=400)

    try:
        history = list(ChatMessage.objects(session_id=session_id).order_by("-created_at")[:6])
        history.reverse()
        ChatMessage(session_id=session_id, role="user", content=question).save()

        conversational_answer = _conversational_reply(question)
        if conversational_answer:
            answer = conversational_answer
            sources = []
        else:
            documents = retrieve(question, limit=5)

        if not conversational_answer and documents:
            answer = generate_answer(question, documents, history)
            seen_urls = set()
            sources = []
            for document in documents:
                if document.url and document.url not in seen_urls:
                    sources.append({"title": document.title, "url": document.url, "type": document.source_type})
                    seen_urls.add(document.url)
                if len(sources) == 3:
                    break
        elif not conversational_answer:
            answer = "I couldn't find that information in Srija's portfolio."
            sources = []
        ChatMessage(session_id=session_id, role="assistant", content=answer, sources=sources).save()
        return JsonResponse({"answer": answer, "sources": sources})
    except AssistantProviderError as exc:
        return JsonResponse({"error": str(exc)}, status=503)
    except Exception:
        return JsonResponse({"error": "The assistant encountered an unexpected problem. Please try again."}, status=500)


@require_POST
@csrf_protect
def clear_history(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid request."}, status=400)
    session_id = str(payload.get("session_id", "")).strip()
    if not SESSION_PATTERN.fullmatch(session_id):
        return JsonResponse({"error": "Invalid chat session."}, status=400)
    ChatMessage.objects(session_id=session_id).delete()
    return JsonResponse({"cleared": True})
