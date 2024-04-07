from argparse import ArgumentParser
from pathlib import Path

from istari.templates.commands import TemplateCommand


class Command(TemplateCommand):
    template_name = 'app_template'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('app_name')
        super().add_arguments(parser)

    def handle(self, **options):
        options['target_dir'] = Path.cwd()
        options['variables'] = {
            'app_name': options['app_name'],
        }

        if not (options['target_dir'] / 'manage.py').is_file():
            raise Exception('File manage.py not found. Please run in root directory of Django project.')
        
        for path in options['target_dir'].rglob('*'):
            if path.is_dir() and (path / 'settings.py').is_file():
                options['target_dir'] = path / 'apps'
                options['target_dir'].mkdir(exist_ok=True)
                break

        return super().handle(**options)
