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

    def process(self, **options):
        raise NotImplementedError(f'{self.__class__.__name__} must implement `.process()`')
