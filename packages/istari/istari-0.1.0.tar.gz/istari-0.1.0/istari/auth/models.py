from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from istari.db.models import UUIDMixin


class User(AbstractUser, UUIDMixin):
    class Meta:
        abstract = True


class EmailUserManager(UserManager):
    def _create_user(self, email: str, username: str | None, password: str | None, **extra_fields):
        '''
        Create and save user with the given email, username, and password.
        '''
        if not email:
            raise ValueError('The given email must be set.')
        email = self.normalize_email(email)
        if username is not None:
            # Load model from app registry versus get_user_model
            # so this manager method can be used in migrations
            GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
            username = GlobalUserModel.normalize_username(username)
        user = self.model(email=email, username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user
        
    def create_user(self, email: str, username: str | None=None, password: str | None=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email: str, username: str | None=None, password: str | None=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, username, password, **extra_fields)


class EmailUser(User):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)

    objects = EmailUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def __str__(self):
        return self.email
    
    def _generate_username(self):
        name = self.get_full_name()
        if len(name) == 0:
            name = self.email.split('@')[0]
        username = slugify(name)
        while self.__class__.objects.filter(username=username).exists():
            username = f'{username}-{get_random_string(length=4)}'
        return username
    
    def save(self, *args, **kwargs):
        if self.username is None:
            self.username = self._generate_username()
        super().save(*args, **kwargs)
