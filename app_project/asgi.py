import os
import sys
from django.core.asgi import get_asgi_application

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_project.settings')
application = get_asgi_application()
