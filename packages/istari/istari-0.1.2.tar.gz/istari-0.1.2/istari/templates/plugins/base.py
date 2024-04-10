from pathlib import Path

from istari.utils.io import File


class BasePlugin:
    help = None

    template = None

    def get_help(self):
        assert self.help is not None, (
            f'{self.__class__.__name__} must define `.help` or implement `.get_help()`'
        )
        return self.help

    def get_template(self):
        assert self.template is not None, (
            f'{self.__class__.__name__} must define `.template` or implement `.get_template()`'
        )
        return self.template

    def add_requirements(self, path: Path, requirements: list[str]):
        f = File(path)
        for requirement in requirements:
            f.append(requirement)
        f.save(sort=True, key=str.casefold)

    def add_settings(self, path: Path, settings: list[str], after: str):
        f = File(path)
        f.seek(after)
        settings.insert(0, '')
        f.insert(settings)
        f.save()

    def process(self, **options):
        raise NotImplementedError(f'{self.__class__.__name__} must implement `.process()`')
