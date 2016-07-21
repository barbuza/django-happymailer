import six
from django.core import mail
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase, TransactionTestCase, override_settings

from dummy.mails import WelcomeTemplate, BasicLayout
from dummy2.mails import DummyTemplate
from .. import Template, t, Layout
from ..models import TemplateModel
from ..utils import (
    template_classes, layout_classes, find_templates,
    TemplateConfigurationError, LayoutNotFound,
)


class BasicsCase(TestCase):
    def test_abstract(self):
        class TestTemplate(Template):
            name = 'foo'
            abstract = True

        with self.assertRaises(AssertionError):
            TestTemplate.check()

        with self.assertRaises(AssertionError):
            TestTemplate('spam')

    def test_defined(self):
        with self.assertRaises(AssertionError):
            class TestTemplate(Template):
                name = 'foo'

            TestTemplate.check()

        with self.assertRaises(AssertionError):
            class TestTemplate2(Template):
                variables = {}

            TestTemplate2.check()

    def test_empty(self):
        class TestTemplate(Template):
            name = 'foo'
            variables = {}

        TemplateModel.objects.create(name='foo', layout='basic')

        tmpl = TestTemplate('spam')
        self.assertDictEqual(tmpl.kwargs, {})

    def test_trafaret(self):
        class TestTemplate(Template):
            name = 'test'
            variables = {'foo': t.Int()}
            kwargs = {'bar': t.String()}

            def get_variables(self):
                return {
                    'foo': int(self.kwargs['bar'])
                }

        TemplateModel.objects.create(name='test', layout='basic')

        tmpl = TestTemplate('spam', bar='1')
        self.assertDictEqual(tmpl.variables, {'foo': 1})

    def test_kwargs(self):
        class TestTemplate(Template):
            name = 'test'
            variables = {}
            kwargs = {'foo': t.String(), 'spam': t.Int()}

        TemplateModel.objects.create(name='test', layout='basic')

        tmpl = TestTemplate('spam', foo='bar', spam=1)
        self.assertDictEqual(tmpl.kwargs, {'foo': 'bar', 'spam': 1})

        with self.assertRaises(t.DataError):
            TestTemplate('spam', foo='bar')

        with self.assertRaises(t.DataError):
            TestTemplate('spam', foo='bar', spam='eggs')

    def test_find_templates(self):

        with override_settings(INSTALLED_APPS=[]):
            self.assertListEqual(template_classes, [])
            self.assertListEqual(layout_classes, [])

        with override_settings(INSTALLED_APPS=['dummy']):
            self.assertListEqual(template_classes, [WelcomeTemplate])
            self.assertListEqual(layout_classes, [BasicLayout])

        with override_settings(INSTALLED_APPS=['dummy2']):
            self.assertListEqual(template_classes, [DummyTemplate])
            self.assertListEqual(layout_classes, [])

        with override_settings(INSTALLED_APPS=['dummy', 'dummy2']):
            self.assertSetEqual(set(template_classes), {WelcomeTemplate, DummyTemplate})
            self.assertSetEqual(set(layout_classes), {BasicLayout})


class EnabledCase(TestCase):
    def test_transaction(self):
        class TestTemplate(Template):
            name = 'test'
            variables = {}

        with self.assertRaises(TemplateConfigurationError):
            TestTemplate('spam')

        model = TemplateModel.objects.create(name='test')

        with self.assertRaises(TemplateConfigurationError):
            TestTemplate('spam')

        model.layout = 'invalid layout'
        model.save()

        with self.assertRaises(LayoutNotFound):
            TestTemplate('spam')

        model.layout = 'basic'
        model.save()

        self.assertFalse(TestTemplate('spam').enabled)

        model.enabled = True
        model.save()

        self.assertTrue(TestTemplate('spam').enabled)


class MigrationCase(TransactionTestCase):
    def test_created(self):
        stdout = six.StringIO()
        call_command('create_email_templates', stdout=stdout)
        self.assertIn('welcome', stdout.getvalue())
        self.assertIn('dummy', stdout.getvalue())
        self.assertTrue(TemplateModel.objects.filter(name='welcome').exists())
        self.assertTrue(TemplateModel.objects.filter(name='dummy').exists())


class HistoryCase(TransactionTestCase):
    def test_version(self):
        model = TemplateModel.objects.create(name='foo')
        self.assertEqual(model.version, 1)

        model.save()
        self.assertEqual(model.version, 1)
        model.refresh_from_db()
        self.assertEqual(model.version, 1)

        model.body = 'spam'
        model.save()
        self.assertEqual(model.version, 2)
        model.refresh_from_db()
        self.assertEqual(model.version, 2)

    def test_history(self):
        with transaction.atomic():
            model = TemplateModel.objects.create(name='foo')

        self.assertEqual(model.historicaltemplate_set.count(), 0)

        with transaction.atomic():
            model.save()

        self.assertEqual(model.historicaltemplate_set.count(), 0)

        with transaction.atomic():
            model.body = 'spam'
            model.save()

        self.assertEqual(model.historicaltemplate_set.count(), 1)


class LayoutCase(TestCase):
    def test_abstract(self):
        class AbstractLayout(Layout):
            abstract = True

        with self.assertRaises(AssertionError):
            AbstractLayout()

    def test_check(self):
        class InvalidLayout(Layout):
            pass

        class AbstractLayout(Layout):
            abstract = True

        class SomeLayout(Layout):
            name = 'some'

        with self.assertRaises(AssertionError):
            InvalidLayout.check()

        self.assertIsNone(AbstractLayout.check())
        self.assertIsNone(SomeLayout.check())

    def test_kwargs(self):
        class TestLayout(Layout):
            kwargs = {'foo': t.String()}

        self.assertDictEqual(TestLayout(foo='bar').kwargs, {'foo': 'bar'})

        with self.assertRaises(t.DataError):
            TestLayout()

    def test_variables(self):
        class TestLayout(Layout):
            kwargs = {'foo': t.String() | t.Int()}
            variables = {'foo': t.String()}

            def get_variables(self):
                return {'foo': self.kwargs['foo']}

        self.assertDictEqual(TestLayout(foo='bar').variables, {'foo': 'bar'})

        with self.assertRaises(t.DataError):
            TestLayout(foo=1)


class ComplexCase(TestCase):
    def test_complex(self):
        class ComplexLayout(Layout):
            name = 'complex'
            kwargs = {'foo': t.String()}
            variables = {'foo': t.String()}

            def render(self, content=None):
                return dict(self.variables)

            def get_variables(self):
                return self.kwargs

        class ComplexTemplate(Template):
            name = 'complex'
            kwargs = {'foo': t.String(), 'spam': t.String()}
            variables = {'spam': t.String()}

            def render(self):
                layout = self.layout_cls(**self.kwargs)
                return layout.render(), dict(self.variables)

            def get_variables(self):
                return {
                    'spam': self.kwargs['spam']
                }

        TemplateModel.objects.create(name='complex', layout='complex')

        find_templates()

        tmpl = ComplexTemplate('spam', foo='bar', spam='eggs')

        layout_render, template_render = tmpl.render()
        self.assertDictEqual(layout_render, {'foo': 'bar'})
        self.assertDictEqual(template_render, {'spam': 'eggs'})


class RenderCase(TestCase):
    def test_render(self):
        class EmptyLayout(Layout):
            name = 'empty'
            content = '{{ body }}'

        class LoopLayout(Layout):
            name = 'loop'
            content = '{% for i in range %}{{ body }}{% endfor %}'
            kwargs = {'count': t.Int()}
            variables = {'range': t.Any()}

            def get_variables(self):
                return {
                    'range': range(self.kwargs['count'])
                }

        class TestTemplate(Template):
            name = 'test'
            variables = {}
            kwargs = {'count': t.Int()}

        find_templates()

        model = TemplateModel.objects.create(name='test', body='', layout='empty')

        tmpl = TestTemplate('spam', count=3)
        self.assertEqual(tmpl.render(), '')

        model.body = 'test'
        model.save()

        tmpl = TestTemplate('spam', count=3)
        self.assertEqual(tmpl.render(), 'test')

        model.layout = 'loop'
        model.save()

        tmpl = TestTemplate('spam', count=3)
        self.assertEqual(tmpl.render(), 'testtesttest')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class CompileCase(TestCase):
    def setUp(self):
        class TestLayout(Layout):
            name = 'test'
            content = '<mjml><mj-body>{{ body }}</mj-body></mjml>'

        class TestTemplate(Template):
            name = 'test'
            variables = {'btn': t.String(), 'name': t.String()}
            kwargs = {'btn': t.String(), 'name': t.String()}

            def get_variables(self):
                return self.kwargs

        TemplateModel.objects.create(
            name='test', layout='test',
            subject='hello, {{ name }}!',
            body='''
            <mj-section>
              <mj-button href="https://github.com/">{{ btn }}</mj-button>
            </mj-section>
            '''
        )

        find_templates()

        self.tmpl = TestTemplate('spam', name='world', btn='foo bar spam eggs')

    def test_compile(self):
        self.assertIn('foo bar spam eggs', self.tmpl.compile())

    def test_send_and_plaintext(self):
        self.tmpl.send(force=True)
        self.assertEqual(mail.outbox[0].subject, 'hello, world!')
        self.assertIn('foo bar spam eggs', mail.outbox[0].body)
        self.assertIn('https://github.com/', mail.outbox[0].body)
