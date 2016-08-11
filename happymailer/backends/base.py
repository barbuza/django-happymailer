class Backend(object):
    def compile(self, source):
        raise NotImplementedError()


class CompileError(Exception):
    pass


class InvalidVariableException(object):
    def __mod__(self, missing):
        raise CompileError('Unknown template variables: %s' % missing)

    def __contains__(self, item):
        if item == '%s':
            return True
        return False