import os
import sys

# Add your project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Tell Django which settings module to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mamefoods.settings')

# Create the WSGI application object
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()