import re
from subprocess import Popen, PIPE

try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata


def version():
    try:
        return 'deepview-converter ' + metadata.version('deepview-converter')
    except Exception:
        try:
            pipe = Popen('git describe --tags --always',
                         stdout=PIPE, shell=True)
            version = str(pipe.communicate()[0].rstrip().decode("utf-8"))
            return 'deepview-converter ' + str(re.sub(r'-g\w+', '', version))
        except Exception:
            return 'deepview-converter unversioned'
