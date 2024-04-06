from pathlib import Path

from istari import BASE_DIR
from istari.cli.commands import BaseCommand


EXCLUDE_DIRS = ['.git', '__pycache__']

EXCLUDE_EXTS = ['.pyc', '.pyo', '.pyd', '.py.class', '.DS_Store']


class TemplateCommand(BaseCommand):
    template_name = None

    def get_template_name(self):
        assert self.template_name is not None, (
            f'{self.__class__.__name__} must define `.template_name` or implement `.get_template_name()`'
        )
        return self.template_name

    def get_target_path(self, template_path: Path) -> Path:
        target_path = str(self.target_dir / template_path.relative_to(self.template_dir))
        for var, val in self.variables.items():
            target_path = target_path.replace(f'{{{{ {var} }}}}', val)
        return Path(target_path)

    def get_path_mappings(self):
        paths = []
        for template_path in self.template_dir.rglob('*'):
            target_path = self.get_target_path(template_path)
            if template_path.is_dir() and target_path.name in self.exclude_dirs:
                continue
            if template_path.is_file() and target_path.name.endswith(tuple(self.exclude_exts)):
                continue
            paths.append((template_path, target_path))
        return paths

    def write_target_file(self, template_path, target_path):
        if target_path.suffix == '.py-tpl':
            target_path = target_path.with_suffix('.py')
        with open(template_path, 'r') as template_file:
            data = template_file.read()
        for var, val in self.variables.items():
            data = data.replace(f'{{{{ {var} }}}}', val)
        with open(target_path, 'w') as target_file:
            target_file.write(data)

    def handle(self, **options):
        self.template_dir = BASE_DIR / 'templates' / self.get_template_name()
        self.target_dir = options.get('target_dir', Path.cwd())
        self.variables = options.get('variables', {})
        self.exclude_dirs = options.get('exclude_dirs', EXCLUDE_DIRS)
        self.exclude_exts = options.get('exclude_exts', EXCLUDE_EXTS)

        paths = self.get_path_mappings()

        for template_path, target_path in paths:
            if target_path.exists():
                path_type = 'File' if template_path.is_file() else 'Directory'
                raise Exception(f'{path_type} {target_path.name} already exists.')
            
        for template_path, target_path in paths:
            if template_path.is_dir():
                target_path.mkdir()
            if template_path.is_file():
                self.write_target_file(template_path, target_path)
