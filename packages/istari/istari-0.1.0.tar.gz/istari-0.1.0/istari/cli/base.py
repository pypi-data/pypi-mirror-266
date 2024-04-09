from argparse import ArgumentParser


class BaseCommand:
    def add_arguments(self, parser: ArgumentParser) -> None:
        return None
    
    def handle(self, **options):
        raise NotImplementedError(f'{self.__class__.__name__} must implement `.handle(self, **options)`')
