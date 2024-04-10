import secrets

def get_random_secret_key():
    '''
    Equivalent to django.core.management.utils.get_random_secret_key
    with the exception of excluding $ from the character set
    '''
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)') for i in range(50))
