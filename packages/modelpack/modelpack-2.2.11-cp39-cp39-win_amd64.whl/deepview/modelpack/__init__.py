import importlib.metadata as metadata
import re
from subprocess import Popen, PIPE


def version():
    try:
        version = metadata.version('modelpack')
        return version
    except Exception:
        try:
            pipe = Popen('git describe --tags --always',
                         stdout=PIPE, shell=True)
            version = str(pipe.communicate()[0].rstrip().decode("utf-8"))
            return str(re.sub(r'-g\w+', '', version))
        except Exception:
            return '0.0.0'
