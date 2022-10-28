import random

import trafaret as t
from django.conf import settings
from faker import Factory

fake = Factory.create(settings.LANGUAGE_CODE)


def generate(trafaret):
    if trafaret is t.Email:
        return fake.email()

    elif trafaret is t.URL:
        return fake.url()

    elif isinstance(trafaret, t.String):
        return fake.name()

    elif isinstance(trafaret, t.Int):
        return random.randint(1, 10)

    elif isinstance(trafaret, t.Float):
        return round(random.uniform(1.0, 100.0), 2)

    elif isinstance(trafaret, t.List):
        res = []
        for i in range(random.randint(1, 5)):
            res.append(generate(trafaret.trafaret))
        return res

    elif isinstance(trafaret, t.Dict):
        res = {}
        for key in trafaret.keys:
            res[key.name] = generate(key.trafaret)
        return res

    elif isinstance(trafaret, t.Or):
        return generate(random.choice(trafaret.trafarets))

    elif isinstance(trafaret, t.Null):
        return

    elif isinstance(trafaret, t.Bool):
        return bool(random.randint(0, 1))

    raise NotImplementedError(repr(trafaret))
