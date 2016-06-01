from django.test import SimpleTestCase

from ..backends import MjmlBackend, CompileError


class MjmlCase(SimpleTestCase):
    def test_mjml(self):
        backend = MjmlBackend()
        backend.compile('<mjml><mj-body><mj-button>foo</mj-button></mj-body></mjml>')

        with self.assertRaises(CompileError):
            backend.compile('foo')
