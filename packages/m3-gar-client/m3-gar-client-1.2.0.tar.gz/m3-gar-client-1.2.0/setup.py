import re
from os.path import (
    abspath,
    dirname,
    join,
)

from pkg_resources import (
    Requirement,
)
from setuptools import (
    find_packages,
    setup,
)


_COMMENT_RE = re.compile(r'(^|\s)+#.*$')


def _get_requirements(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = _COMMENT_RE.sub('', line)
            line = line.strip()

            if line.startswith('-r '):
                for req in _get_requirements(join(dirname(abspath(file_path)), line[3:])):
                    yield req

            elif line:
                req = Requirement(line)
                req_str = req.name + str(req.specifier)

                if req.marker:
                    req_str += '; ' + str(req.marker)

                yield req_str


def _read(file_path):
    with open(file_path, 'r') as infile:
        return infile.read()


setup(
    name='m3-gar-client',
    url='https://stash.bars-open.ru/projects/M3/repos/m3-gar-client',
    license='MIT',
    author='BARS Group',
    description=u'UI клиент для сервера ГАР m3-rest-gar',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=('testapp', 'testapp.*',)),
    long_description=_read('README.rst'),
    long_description_content_type='text/x-rst',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
    ],
    install_requires=tuple(_get_requirements('requirements/prod.txt')),
    extras_require={
        'oauth2': (
            'oauthlib>=2,<3.3',
            'requests-oauthlib<=1.3.1',
        ),
        'm3': (
            'm3-core>=2.2.16,<4',
            'm3-ui>=2.0.8,<3'
        ),
        'rest': (
            'djangorestframework',
        )
    },
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.2,<2',
    ),
    python_requires='>=3.6',
    set_build_info=dirname(__file__),
)
