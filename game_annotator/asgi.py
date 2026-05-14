"""
ASGI config for game_annotator project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_annotator.settings')

application = get_asgi_application()
