from pathlib import Path

from istari.constants import BASE_DIR
from istari.templates.plugins.base import BasePlugin


class Plugin(BasePlugin):
    help = 'Install istari in editable mode'

    template = 'project'

    def append_to_compose_volumes(self, value: str, path: Path) -> None:
        with open(path, 'r') as f:
            contents = f.readlines()    
        fp = 0
        for i, line in enumerate(contents):
            if line.lstrip().startswith('volumes'):
                fp = i + 1
                break
        pad = len(contents[fp]) - len(contents[fp].lstrip(' '))
        while contents[fp].lstrip().startswith('-'):
            fp += 1
        contents.insert(fp, f"{pad * ' '}- {value}\n")
        with open(path, 'w') as f:
            f.writelines(contents)

    def append_to_makefile_command(self, command: str, value: str, path: Path) -> None:
        with open(path, 'r') as f:
            contents = f.readlines()
        fp = 0
        for i, line in enumerate(contents):
            if line.startswith(f'.PHONY: {command}'):
                fp = i + 1
                break
        while not contents[fp].startswith('.PHONY'):
            fp += 1
        fp -= 1
        contents.insert(fp, f"\t{value}\n")
        with open(path, 'w') as f:
            f.writelines(contents)

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
