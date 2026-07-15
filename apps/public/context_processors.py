# apps/public/context_processors.py

from .models import Profile, ResumeFile
from datetime import datetime

def global_context(request):
    """Add global context variables to all templates"""
    try:
        profile = Profile.objects.first()
    except:
        profile = None

    try:
        active_resume = ResumeFile.objects(is_active=True).first()
    except Exception:
        active_resume = None
    
    return {
        'profile': profile,
        'active_resume': active_resume,
        'current_year': datetime.now().year,
    }
