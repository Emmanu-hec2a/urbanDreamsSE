from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale
from .utils import broadcast_dashboard_update

@receiver(post_save, sender=Sale)
def notify_dashboard(sender, instance, created, **kwargs):
    if created:
        broadcast_dashboard_update()
