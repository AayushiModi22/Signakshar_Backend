#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
# import os
# import sys


# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hastakshar_backend.settings')
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)


# if __name__ == '__main__':
#     main()

import os
import sys
import subprocess
from threading import Thread

def run_command(command):
    subprocess.run(command, shell=True)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hastakshar_backend.settings')
    
    if 'runserver' in sys.argv:
        # Commands to run concurrently
        commands = [
            "celery -A hastakshar_backend.celery worker --pool=solo -l info",
            "celery -A hastakshar_backend beat -l info"
        ]

        # Start a thread for each command
        threads = [Thread(target=run_command, args=(cmd,)) for cmd in commands]
        for thread in threads:
            thread.start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
