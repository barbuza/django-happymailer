import logging

from django.core.signals import setting_changed
from django.db import models
from django.db import transaction
from django.dispatch import receiver

from .models import TemplateModel
from .utils import find_templates

logger = logging.getLogger(__name__)


@receiver(models.signals.post_init, sender=TemplateModel)
@receiver(models.signals.post_save, sender=TemplateModel)
def update_db_state(instance, **kwargs):
    instance.db_subject = instance.subject
    instance.db_body = instance.body
    instance.db_layout = instance.layout
    instance.db_version = instance.version


@receiver(models.signals.pre_save, sender=TemplateModel)
def update_history(instance, **kwargs):
    if instance.body != instance.db_body \
            or instance.layout != instance.db_layout \
            or instance.subject != instance.db_subject:
        instance.version += 1

    if instance.version != instance.db_version:
        version = instance.version

        @transaction.on_commit
        def save():
            instance.history.create(
                version=version,
                body=instance.body,
                subject=instance.subject,
                layout=instance.layout,
            )


@receiver(setting_changed)
def reload_templates(**kwargs):
    find_templates()
