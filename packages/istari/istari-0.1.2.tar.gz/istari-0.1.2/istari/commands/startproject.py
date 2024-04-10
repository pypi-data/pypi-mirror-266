from argparse import ArgumentParser

from istari import __version__
from istari.constants import SECRET_KEY_INSECURE_PREFIX
from istari.templates.commands import TemplateCommand
from istari.utils import get_random_secret_key


class Command(TemplateCommand):
    template_name = 'project_template'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('project_name')
        super().add_arguments(parser)
    
    def handle(self, **options):
        options['variables'] = {
            'docs_version': '5.0',
            'istari_version': __version__,
            'project_name': options['project_name'],
            'secret_key': SECRET_KEY_INSECURE_PREFIX + get_random_secret_key(),
        }
        return super().handle(**options)
