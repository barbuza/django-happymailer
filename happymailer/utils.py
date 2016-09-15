import os.path

import trafaret
from django.apps import apps
from django.utils.module_loading import import_module

from . import fake
from .backends.base import CompileError

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


def template_compile_check(cls):
    kwargs = fake.generate(cls.kwargs)
    variables = cls.fake_variables()
    variables = {x.name: render_python_key(x, variables) for x in cls.variables.keys}
    instance = cls(None, _force_variables=variables, **kwargs)

    try:
        instance.compile()
    except CompileError as e:
        model = instance.model
        model.has_error = True
        model.enabled = False
        model.save_base(raw=True)
        raise


def render_python_key(x, variables=None):
    if variables is None:
        variables = {}

    if isinstance(x.trafaret, trafaret.Dict):
        value = {k.name: render_python_key(k, variables.get(x.name)) for k in x.trafaret.keys}
    else:
        value = variables.get(x.name, fake.generate(x.trafaret))

    return value


def render_react_key(x, variables=None):
    if variables is None:
        variables = {}

    if isinstance(x.trafaret, trafaret.Dict):
        value = [render_react_key(k, variables.get(x.name)) for k in x.trafaret.keys]
    else:
        value = variables.get(x.name, fake.generate(x.trafaret))

    return {
        'name': x.name,
        'type': repr(x.trafaret),
        'value': value,
        'valueType': x.trafaret.__class__.__name__.lower()
    }
