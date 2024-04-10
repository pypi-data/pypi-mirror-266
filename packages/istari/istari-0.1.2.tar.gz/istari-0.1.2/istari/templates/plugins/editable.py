from pathlib import Path

from istari.constants import BASE_DIR
from istari.templates.plugins.base import BasePlugin
from istari.utils.io import File


class Plugin(BasePlugin):
    help = 'Install istari in editable mode'

    template = 'project'

    def append_to_compose_volumes(self, value: str, path: Path) -> None:
        f = File(path)
        f.seek('volumes')
        while f.contents[f.fp].lstrip().startswith('-'):
            f.fp += 1
        f.insert(f'- {value}')
        f.save()

    def append_to_makefile_command(self, command: str, value: str, path: Path) -> None:
        f = File(path)
        f.seek(f'.PHONY: {command}')
        while not f.contents[f.fp].startswith('.PHONY'):
            f.fp += 1
        f.fp -= 1
        f.insert(f'\t{value}')
        f.save()

    def process(self, **options):
        target_dir = options['target_dir']
        self.append_to_compose_volumes(
            f'{BASE_DIR.parent}:/usr/app/istari',
            target_dir / 'compose.yaml',
        )
        self.append_to_makefile_command(
            'up',
            'docker exec -it ${NAME}_django pip install -e /usr/app/istari',
            target_dir / 'Makefile'
        )
