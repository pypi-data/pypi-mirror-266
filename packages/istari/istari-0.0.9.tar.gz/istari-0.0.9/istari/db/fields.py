import uuid
from django.core.exceptions import ValidationError
from django.db import models


class AutoCreatedField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_now_add', True)
        super().__init__(*args, **kwargs)


class AutoLastModifiedField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('auto_now', True)
        super().__init__(*args, **kwargs)


class UUIDField(models.UUIDField):
    def __init__(self, primary_key=False, version=4, editable=False, *args, **kwargs):
        if version == 2:
            raise ValidationError('UUID version 2 is not supported.')
        
        if version < 1 or version > 5:
            raise ValidationError('UUID version is not valid.')
        
        if version == 1:
            default = uuid.uuid1
        elif version == 3:
            default = uuid.uuid3
        elif version == 4:
            default = uuid.uuid4
        elif version == 5:
            default == uuid.uuid5

        kwargs.setdefault('primary_key', primary_key)
        kwargs.setdefault('default', default)
        kwargs.setdefault('editable', editable)
        super().__init__(*args, **kwargs)
