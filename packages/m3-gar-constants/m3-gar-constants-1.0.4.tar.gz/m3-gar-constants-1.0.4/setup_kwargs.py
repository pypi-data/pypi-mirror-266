import codecs
from pathlib import (
    Path,
)

from m3_gar_constants.version import (
    __version__,
)


def read(fn):
    return codecs.open(Path(__file__).resolve().parent / fn).read()


setup_kwargs = dict(
    name='m3-gar-constants',
    version=__version__,
    author='BARS Group',
    author_email='bars@bars.group',
    description='GAR constants for m3',
    long_description=read('README.rst'),
    license='MIT license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
