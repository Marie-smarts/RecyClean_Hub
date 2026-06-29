from django.contrib.auth.models import User


def username_from_email(email):
    """Generate a unique username from an email address."""
    base = email.split('@')[0].lower().replace('.', '_').replace('+', '_')[:30]
    if not base:
        base = 'user'
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        username = f'{base}{suffix}'
        suffix += 1
    return username
