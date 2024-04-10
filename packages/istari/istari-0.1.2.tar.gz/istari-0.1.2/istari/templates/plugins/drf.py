from pathlib import Path

from istari.templates.plugins.base import BasePlugin


class Plugin(BasePlugin):
    help = 'Install Django Rest Framework'

    template = 'project'

    def process(self, **options):
        target_dir = options['target_dir']
        self.add_requirements(target_dir / 'requirements.txt', [
            'djangorestframework==3.14.0',
            'djangorestframework-simplejwt==5.3.1',
            'PyJWT==2.8.0',
            'pytz==2023.4',
        ])
        self.add_settings(target_dir / options['project_name'] / 'settings.py', [
            "REST_FRAMEWORK = {",
            "    'DEFAULT_AUTHENTICATION_CLASSES': (",
            "        'rest_framework_simplejwt.authentication.JWTAuthentication',",
            "    ),",
            "    'DEFAULT_PERMISSION_CLASSES': [",
            "        'rest_framework.permissions.IsAuthenticated',",
            "    ],",
            "}",
            "",
            "SIMPLE_JWT = {",
            "    'USER_ID_FIELD': 'uuid',",
            "    'USER_ID_CLAIM': 'uuid',",
            "}", 
        ], 'WSGI_APPLICATION')
