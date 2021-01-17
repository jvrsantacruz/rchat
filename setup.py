import io
import re
from setuptools import setup, find_packages


def get_version_from_debian_changelog():
    try:
        with io.open('debian/changelog', encoding='utf8') as stream:
            return re.search(r'\((.+)\)', next(stream)).group(1)
    except Exception:
        return '0.0.1'


setup(
    name='rchat',
    description='A simple RocketChat command line client',
    long_description=io.open('README.md').read(),
    long_description_content_type='text/markdown',
    version=get_version_from_debian_changelog(),
    include_package_data=True,
    author='Javier Santacruz',
    author_email='javier.santacruz.lc@gmail.com',
    url='https://github.com/jvrsantacruz/rchat',
    install_requires=io.open('requirements.txt').read().splitlines(),
    license='GPL3',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'rchat = rchat.cli:cli',
        ]
    },
    classifiers=(
        'Topic :: Communications :: Chat',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.8',
    ),
)
