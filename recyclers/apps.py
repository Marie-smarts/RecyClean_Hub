from django.apps import AppConfig


class RecyclersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recyclers'
    verbose_name = 'Recycling Companies'

    def ready(self):
        import recyclers.signals  # noqa: F401
