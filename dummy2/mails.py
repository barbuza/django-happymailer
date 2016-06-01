from happymailer import Template, t


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
