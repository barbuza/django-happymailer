import os.path
import subprocess

from django.conf import settings

from .base import Backend, CompileError


class MjmlBackend(Backend):
    def compile(self, source):
        command = ['-i', '-s']
        if isinstance(settings.HAPPYMAILER_MJML_BIN, list):
            command = [os.path.expanduser(x) for x in settings.HAPPYMAILER_MJML_BIN] + command
        else:
            command.insert(0, os.path.expanduser(settings.HAPPYMAILER_MJML_BIN))
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = proc.communicate(source.encode('utf-8'))
        out = out.decode('utf-8')
        if proc.returncode:
            raise CompileError(out)
        if 'node_modules/mjml' in out:
            raise CompileError(out)
        return out
