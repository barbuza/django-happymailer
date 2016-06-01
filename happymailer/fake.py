import random

import trafaret as t
from django.conf import settings
from faker import Factory

fake = Factory.create(settings.LANGUAGE_CODE)


def generate(trafaret):
    if isinstance(trafaret, t.Email):
        return fake.email()
    elif isinstance(trafaret, t.URL):
        return fake.url()
    elif isinstance(trafaret, t.String):
        return fake.name()
    elif isinstance(trafaret, t.Int):
        return random.randint(1, 10)
    elif isinstance(trafaret, t.List):
        res = []
        for i in range(random.randint(1, 10)):
            res.append(generate(trafaret.trafaret))
        return res
    elif isinstance(trafaret, t.Dict):
        res = {}
        for key in trafaret.keys:
            res[key.name] = generate(key.trafaret)
        return res

    raise NotImplementedError(repr(trafaret))
