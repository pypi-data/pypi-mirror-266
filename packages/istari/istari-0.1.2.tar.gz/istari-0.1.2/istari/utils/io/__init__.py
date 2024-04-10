from pathlib import Path


class File:
    def __init__(self, path: Path):
        self.path = path
        self.contents = self.readlines()
        self.fp = 0

    def readlines(self):
        with open(self.path, 'r') as f:
            return f.readlines()

    def calculate_left_pad(self, line: str, char=' ') -> int:
        return len(line) - len(line.lstrip(char))

    def seek(self, prefix):
        for i, line in enumerate(self.contents, start=self.fp):
            if line.lstrip().startswith(prefix):
                self.fp = i + 1
                break
        self.pad = self.calculate_left_pad(self.contents[self.fp])

    def append(self, line):
        self.contents.append(line.rstrip('\n') + '\n')

    def _insert(self, line):
        line = line.rstrip('\n') + '\n'
        self.contents.insert(self.fp, f"{self.pad * ' '}{line}")
        self.fp += 1

    def insert(self, line):
        if type(line) is list:
            for l in line:
                self._insert(l)
        else:
            self._insert(line)

    def save(self, **kwargs):
        sort = kwargs.setdefault('sort', False)
        if sort is True:
            assert 'key' in kwargs, (
                f'{self.__class__.__name__}.save() must define a key attriuute if sort=True'
            )
            self.contents = sorted(self.contents, key=kwargs['key'])
        with open(self.path, 'w') as f:
            f.writelines(self.contents)
