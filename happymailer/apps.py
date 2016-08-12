from django.apps import AppConfig

__all__ = ('HappyMailerConfig',)


class HappymailerConfig(AppConfig):
    name = 'happymailer'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import receivers
        from .utils import find_templates, all_template_classes, all_layout_classes
        find_templates()
        for cls in all_template_classes:
            cls.check()
        for cls in all_layout_classes:
            cls.check()
