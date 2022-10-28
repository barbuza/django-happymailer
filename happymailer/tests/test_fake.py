import six
import trafaret as t
from django.test import SimpleTestCase

from ..fake import generate


class FakeCase(SimpleTestCase):
    def test_string(self):
        self.assertIsInstance(generate(t.String()), six.text_type)

    def test_email(self):
        self.assertIn('@', generate(t.Email))

    def test_url(self):
        self.assertIn('://', generate(t.URL))

    def test_int(self):
        self.assertIsInstance(generate(t.Int()), int)

    def test_list(self):
        lst = generate(t.List[t.String()])
        self.assertIsInstance(lst, list)
        for i in lst:
            self.assertIsInstance(i, six.text_type)

    def test_dict(self):
        dct = generate(t.Dict(foo=t.String(), bar=t.Int()))
        self.assertSetEqual(set(dct.keys()), {'foo', 'bar'})
        self.assertIsInstance(dct['foo'], six.text_type)
        self.assertIsInstance(dct['bar'], int)
