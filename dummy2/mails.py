from happymailer import Template, t
from happymailer.fake import fake


class DummyTemplate(Template):
    name = 'dummy'
    layout = 'basic'

    kwargs = variables = {
        'name': t.String(),
        'code': t.String(),
        'email': t.Email()
    }

    def get_variables(self):
        return self.kwargs

    @classmethod
    def fake_variables(cls):
        return {
            'code': fake.ean()
        }
