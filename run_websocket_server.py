#!/usr/bin/env python
"""
Script to run Django development server with WebSocket support.

For development, you can use this script or run:
    python manage.py runserver

For production, use:
    daphne -b 0.0.0.0 -p 8000 mentorship_platform.asgi:application
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentorship_platform.settings')

if __name__ == '__main__':
    # Run the development server
    execute_from_command_line(sys.argv, ['manage.py', 'runserver', '--noreload'])