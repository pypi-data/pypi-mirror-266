from setuptools import setup


setup(
    name             = 'Torrelque',
    version          = '0.7.0',
    author           = 'saaj',
    author_email     = 'mail@saaj.me',
    packages         = ['torrelque'],
    package_data     = {'torrelque' : ['*.lua']},
    license          = 'LGPL-3.0-only',
    description      = 'Asynchronous Redis-backed reliable queue package',
    long_description = open('README.rst', 'rb').read().decode('utf-8'),
    platforms        = ['Any'],
    python_requires  = '>= 3',
    keywords         = 'python redis asynchronous job-queue work-queue',
    url              = 'https://heptapod.host/saajns/torrelque',
    project_urls     = {
        'Source Code'   : 'https://heptapod.host/saajns/torrelque',
        'Documentation' : 'https://torrelque.readthedocs.io/',
        'Release Notes' : 'https://torrelque.readthedocs.io/en/latest/history.html',
    },
    classifiers = [
        'Topic :: Software Development :: Libraries',
        'Framework :: AsyncIO',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
    ],
    install_requires = ['redis >= 5.0.1'],
    extras_require   = {
        'manual' : ['sphinx >= 7, < 8'],
    },
)
