import importlib
import pkgutil
from argparse import ArgumentParser

from istari.cli.commands import BaseCommand


class IstariCLI:
    def __init__(self):
        self.parser = ArgumentParser()
        self.subparsers = self.parser.add_subparsers(title='commands', dest='command_name')
        self.subparsers.required = True

        self.command_map: dict[str, BaseCommand] = {}
        self.process_commands()

    def run(self):
        args = self.parser.parse_args().__dict__
        command_name = args.pop('command_name')
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
