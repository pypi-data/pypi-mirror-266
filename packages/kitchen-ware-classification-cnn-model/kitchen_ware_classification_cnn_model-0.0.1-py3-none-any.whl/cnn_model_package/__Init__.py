import os

from cnn_model_package.config.core import PACKAGE_ROOT

with open(os.path.join(PACKAGE_ROOT, 'VERSION')) as _version_file:
    __version__ = _version_file.read().strip()