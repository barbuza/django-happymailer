from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    create db templates
    """
    can_import_settings = True
    requires_system_checks = True
    output_transaction = True

    def handle(self, *args, **options):
        from ...utils import template_classes
        from ...models import TemplateModel
        for cls in template_classes:
            if not TemplateModel.objects.filter(name=cls.name).exists():
                try:
                    cls.check()
                except AssertionError:
                    pass
                else:
                    self.stdout.write('create {} ({}.{})\n'.format(cls.name, cls.__module__, cls.__name__))
                    TemplateModel.objects.create(name=cls.name)
