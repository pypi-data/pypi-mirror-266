from argparse import ArgumentParser
from pathlib import Path

from istari.templates.commands import TemplateCommand


class Command(TemplateCommand):
    template_name = 'app_template'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('app_name')
        super().add_arguments(parser)

    def sort_installed_apps(self, apps: list[str]) -> list[str]:
        '''
        Sort INSTALLED_APPS by alphabetically
        sorting any apps that start with 'apps'
        '''
        start = [i for i, a in enumerate(apps) if a.startswith("'apps")][0]
        return apps[:start] + sorted(apps[start:])

    def append_installed_apps(self, settings: Path, app_name: str):
        with open(settings, 'r') as f:
            contents = f.readlines()

        # append app to INSTALLED_APPS
        start = 0
        for i, line in enumerate(contents):
            if line.startswith('INSTALLED_APPS'):
                start = i + 1
                break
        end = start
        while not contents[end].startswith(']'):
            end += 1
        contents.insert(end, f"    'apps.{app_name}',\n")
        end += 1

        # sort alphabetically
        apps = self.sort_installed_apps([app.strip() for app in contents[start:end]])
        del contents[start:end]
        for app in reversed(apps):
            contents.insert(start, f'    {app}\n')

        with open(settings, 'w') as f:
            f.writelines(contents)

    def handle(self, **options):
        options['target_dir'] = options.get('target_dir', Path.cwd())
        options['variables'] = {
            'app_name': options['app_name'],
        }

        if not (options['target_dir'] / 'manage.py').is_file():
            raise Exception('File manage.py not found. Please run in root directory of Django project.')
        
        settings = None
        for path in options['target_dir'].rglob('*'):
            if path.is_dir() and (path / 'settings.py').is_file():
                settings = path / 'settings.py'
                options['target_dir'] = path / 'apps'
                options['target_dir'].mkdir(exist_ok=True)
                break

        self.append_installed_apps(settings, options['app_name'])
        return super().handle(**options)
