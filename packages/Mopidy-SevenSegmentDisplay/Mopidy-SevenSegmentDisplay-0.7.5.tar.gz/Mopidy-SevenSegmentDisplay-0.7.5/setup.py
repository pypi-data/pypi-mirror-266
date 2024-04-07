import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-SevenSegmentDisplay',
    version=get_version('mopidy_sevensegmentdisplay/__init__.py'),
    url='https://github.com/JumalIO/mopidy-sevensegmentdisplay',
    license='Apache License, Version 2.0',
    author='Julius',
    author_email='spamjulius@mail.com',
    maintainer='Julius',
    maintainer_email='spamjulius@mail.com',
    description='A Mopidy extension for using it with seven segment display.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    python_requires='>= 3.7',
    install_requires=[
        'setuptools',
        'Mopidy >= 3.0',
        'Pykka >= 1.1',
        'monotonic >= 1.4',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'sevensegmentdisplay = mopidy_sevensegmentdisplay:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
