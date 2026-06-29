from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='aggregators.CollectionLog')
def on_collection_logged(sender, instance, created, **kwargs):
    if created:
        from .services import link_traceability_for_collection

        link_traceability_for_collection(instance)
