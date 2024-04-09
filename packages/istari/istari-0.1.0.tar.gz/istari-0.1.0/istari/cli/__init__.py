import importlib
import pkgutil
import sys
from argparse import ArgumentParser
from gettext import gettext as _

from istari import __version__
from istari.cli.base import BaseCommand


class CustomParser(ArgumentParser):
    def error(self, message):
        if message.startswith('argument command_name: invalid choice'):
            return

        if message.startswith('unrecognized arguments'):
            return

        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)


class IstariCLI:
    def __init__(self):
        self.parser = CustomParser()
        self.parser.add_argument('-v', '--version', action='store_true')
        self.subparsers = self.parser.add_subparsers(title='commands', dest='command_name')

        self.command_map: dict[str, BaseCommand] = {}
        self.process_commands()

    def run(self):
        args = self.parser.parse_args().__dict__

        if args.pop('version', False):
            print(__version__)
            return

        command_name = args.pop('command_name', None)
        if command_name is None:
            print('\nAvailable commands:\n')
            for command in self.command_map.keys():
                print(command)
            print('')
            return

        self.command_map[command_name].handle(**args)

    def process_commands(self):
        self.command_map = self.get_commands('istari.commands')
        for name, instance in self.command_map.items():
            command_parser = self.subparsers.add_parser(name)
            instance.add_arguments(command_parser)

    def get_commands(self, module_name: str) -> dict[str, BaseCommand]:
        return {
            command_name: self.load_command_class(f'{module_name}.{command_name}')
            for _, command_name, ispkg in pkgutil.iter_modules(importlib.import_module(module_name).__path__)
            if not ispkg and not command_name.startswith('_')
        }
    
    def load_command_class(self, module_name: str) -> BaseCommand:
        module = importlib.import_module(module_name)
        command_class = getattr(module, 'Command')
        return command_class()


def main():
    IstariCLI().run()
