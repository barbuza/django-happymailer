import logging

import html2text
import six
import trafaret as t
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template as DjangoTemplate, Context
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

from . import fake
from .backends.base import InvalidVariableException
from .utils import all_template_classes, all_layout_classes, get_layout, TemplateConfigurationError

default_app_config = 'happymailer.apps.HappymailerConfig'


__all__ = ('Template', 'Layout', 't')

logger = logging.getLogger(__name__)


class BasicMeta(type):
    registry = []
    ignore_extra = False

    def __new__(mcs, name, bases, dct):
        dct.setdefault('abstract', False)
        abstract = dct['abstract']

        base_variables = t.Dict({})

        for klass in bases:
            variables = getattr(klass, 'variables', None)
            if variables:
                base_variables = base_variables.merge(variables)

        if 'kwargs' in dct:
            kwargs = dct.pop('kwargs')
            if not abstract or kwargs is not None:
                assert isinstance(kwargs, dict)
                kwargs = t.Dict(**kwargs)
                if mcs.ignore_extra:
                    kwargs = kwargs.ignore_extra('*')

            dct.update(kwargs=kwargs)

        if 'variables' in dct:
            variables = dct.pop('variables')
            if not abstract or variables is not None:
                assert isinstance(variables, dict)
                variables = base_variables.merge(variables)
                if mcs.ignore_extra:
                    variables = variables.ignore_extra('*')

            dct.update(variables=variables)

        cls = type.__new__(mcs, name, bases, dct)

        if not abstract:
            mcs.registry.append(cls)

        return cls


class LayoutMeta(BasicMeta):
    registry = all_layout_classes
    ignore_extra = True


class TemplateMeta(BasicMeta):
    registry = all_template_classes


class MessageMeta(BasicMeta):
    pass


class Layout(six.with_metaclass(LayoutMeta)):
    name = None
    description = None
    abstract = True
    variables = {}
    content = None

    def __init__(self):
        assert not self.abstract
        self.variables = self.variables.check(self.get_variables())

    def get_variables(self):
        return {}

    def render(self, content):
        pass

    @classmethod
    def check(cls):
        if cls.abstract:
            assert not cls.name, 'abstract layout {}.{} must not have a name'.format(cls.__module__, cls.__name__)
        else:
            assert cls.name


class Template(six.with_metaclass(TemplateMeta)):
    name = None
    variables = None
    kwargs = {}
    abstract = True

    def __init__(self, recipient=None, _force_layout_cls=None, _force_variables=None, **kwargs):
        assert not self.abstract

        self._recipients = []
        if recipient:
            self._recipients.append(recipient)

        if _force_layout_cls:
            self.layout_cls = _force_layout_cls
        else:
            self.layout_cls = None
            if self.layout:
                self.layout_cls = get_layout(self.layout)

        if not self.layout_cls:
            raise TemplateConfigurationError('no layout specified for {} template'.format(self.name))

        self.kwargs = self.kwargs.check(kwargs)

        if _force_variables:
            self.variables = _force_variables
        else:
            self.post_init()
            self.variables = self.variables.check(self.get_variables())

    def post_init(self):
        pass

    def add_recipient(self, recipient):
        self._recipients.append(recipient)

    def recipients(self):
        return self._recipients

    @classmethod
    def fake_variables(cls):
        return fake.generate(cls.variables)

    @classmethod
    def fake_kwargs(cls):
        return fake.generate(cls.kwargs)

    @cached_property
    def model(self):
        from .models import TemplateModel
        return TemplateModel.objects.filter(name=self.name).first()

    @cached_property
    def layout(self):
        return self.model.layout if self.model else None

    @cached_property
    def subject(self):
        return self.model.subject if self.model else None

    @cached_property
    def enabled(self):
        return self.model.enabled if self.model else None

    @cached_property
    def body(self):
        return self.model.body if self.model else None

    def get_variables(self):
        return {}

    def render(self):
        layout = self.layout_cls()
        dj_tmpl = DjangoTemplate(self.body)
        dj_tmpl.engine.string_if_invalid = InvalidVariableException()
        body = dj_tmpl.render(Context(self.variables))
        dj_tmpl.engine.string_if_invalid = ''
        return six.text_type(DjangoTemplate(layout.content).render(Context(dict(layout.variables, body=body))))

    def compile(self):
        backend_cls = import_string(settings.HAPPYMAILER_BACKEND)
        backend = backend_cls()
        return backend.compile(self.render())

    def send(self, force=False):
        if not self.enabled and not force:
            return
        subject = six.text_type(DjangoTemplate(self.subject).render(Context(self.variables)))
        html = self.compile()
        text = html2text.html2text(html)
        self._send(subject, text, settings.HAPPYMAILER_FROM, recipient_list=self.recipients(),
                   html_message=html, fail_silently=False)

    def _send(self, subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None):
        send_mail(subject, message, from_email, recipient_list,
                  fail_silently, auth_user, auth_password,
                  connection, html_message)

    @classmethod
    def check(cls):
        if cls.abstract:
            assert not cls.name, 'abstract template {}.{} must not have a name'.format(cls.__module__, cls.__name__)
        else:
            assert cls.name
            assert cls.variables
            assert cls.kwargs
