import secrets
from pathlib import Path

__version__ = '0.0.5'

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY_INSECURE_PREFIX = 'django-insecure'

def get_random_secret_key():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)') for i in range(50))
