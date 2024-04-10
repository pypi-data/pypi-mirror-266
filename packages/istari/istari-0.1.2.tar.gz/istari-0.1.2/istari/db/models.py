from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from istari.db.fields import AutoCreatedField, AutoLastModifiedField, UUIDField


class SlugMixin(models.Model):
    slug = models.SlugField()

    SLUG_FIELD = 'name'

    def slugify(self):
        return slugify(getattr(self, self.SLUG_FIELD))
    
    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = self.slugify()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', None)
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields).union('updated_at')
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    uuid = UUIDField(_('UUID'))

    class Meta:
        abstract = True


class SlugModel(SlugMixin, TimeStampedMixin):
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True


class UUIDModel(TimeStampedMixin, UUIDMixin):
    class Meta:
        abstract = True
