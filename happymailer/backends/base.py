class Backend(object):
    def compile(self, source):
        raise NotImplementedError()


class CompileError(Exception):
    pass
