from django.apps import AppConfig


class DjangoAutoTimestampsModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_auto_timestamps_model'