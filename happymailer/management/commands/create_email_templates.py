from django.core.management.base import BaseCommand
from ...utils import template_compile_check
from ...backends.base import CompileError

class Command(BaseCommand):
    """
    create db templates
    """
    can_import_settings = True
    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument('--no-check', action='store_true', dest='no_check', default=False,
                            help='disable templates compile check')

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

            if not options.get('no_check'):
                try:
                    template_compile_check(cls)
                except CompileError as e:
                    self.stdout.write('{} got compile error: {}'.format(cls.name, str(e)))