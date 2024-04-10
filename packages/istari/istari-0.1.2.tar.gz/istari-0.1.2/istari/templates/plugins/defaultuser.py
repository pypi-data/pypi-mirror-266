from pathlib import Path

from istari.commands.startapp import Command as StartAppCommand
from istari.templates.plugins.base import BasePlugin
from istari.utils.io import File


class Plugin(BasePlugin):
    help = 'Define custom AUTH_USER_MODEL'

    template = 'project'

    def create_users_app(self):
        StartAppCommand().handle(app_name='users', target_dir=self.target_dir, ignore_plugins=True)

    def add_users_model(self):
        path = self.target_dir / self.project_name / 'apps' / 'users' / 'models.py'
        contents = [
            'from django.db import models\n',
            '\n',
            'from istari.auth.models import EmailUser\n',
            '\n',
            '\n',
            'class User(EmailUser):\n',
            '    pass\n',
        ]
        with open(path, 'w') as f:
            f.writelines(contents)

    def define_auth_user_model(self):
        f = File(self.target_dir / self.project_name / 'settings.py')
        f.seek('ALLOWED_HOSTS')
        f.insert([
            '',
            "AUTH_USER_MODEL = 'users.User'",
        ])
        f.save()

    def process(self, **options):
        self.project_name: str = options['project_name']
        self.target_dir: Path = options['target_dir']
        self.create_users_app()
        self.add_users_model()
        self.define_auth_user_model()
