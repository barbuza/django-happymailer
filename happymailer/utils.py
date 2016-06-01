import os.path

from django.apps import apps
from django.utils.module_loading import import_module

__all__ = ('all_template_classes', 'template_classes', 'all_layout_classes',
           'layout_classes', 'find_templates', 'get_layout', 'get_template',
           'TemplateConfigurationError')

all_layout_classes = []
layout_classes = []

all_template_classes = []
template_classes = []


class EmailError(Exception):
    pass


class LayoutNotFound(EmailError):
    pass


class TemplateNotFound(EmailError):
    pass


class TemplateConfigurationError(EmailError):
    pass


def get_layout(name):
    for cls in layout_classes:
        if cls.name == name:
            return cls
    raise LayoutNotFound(name)


def get_template(name):
    for cls in template_classes:
        if cls.name == name:
            return cls
    raise TemplateNotFound(name)


def in_module(cls, module):
    if cls.__module__ == module.__name__:
        return True
    return cls.__module__.startswith('{}.'.format(module.__name__))


def find_templates():
    template_classes.clear()
    layout_classes.clear()

    for app in apps.get_app_configs():
        if os.path.isfile(os.path.join(app.path, 'mails.py')):
            import_module('{}.mails'.format(app.name))

    for cls in all_template_classes:
        if cls.abstract:
            continue
        found = False
        for app in apps.get_app_configs():
            if in_module(cls, app.module):
                found = True
                break
        if found:
            template_classes.append(cls)

    for cls in all_layout_classes:
        if cls.abstract:
            continue
        found = False
        for app in apps.get_app_configs():
            if in_module(cls, app.module):
                found = True
                break
        if found:
            layout_classes.append(cls)
