from django.apps import AppConfig

class ProductManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product_manager'

    def ready(self):
        import product_manager.signals