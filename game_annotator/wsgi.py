"""
WSGI config for game_annotator project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_annotator.settings')

application = get_wsgi_application()
