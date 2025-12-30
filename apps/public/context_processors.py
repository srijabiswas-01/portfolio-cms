# apps/public/context_processors.py

from .models import Profile
from datetime import datetime

def global_context(request):
    """Add global context variables to all templates"""
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    return {
        'profile': profile,
        'current_year': datetime.now().year,
    }