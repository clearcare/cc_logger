from setuptools import setup, find_packages

setup(
    name = 'cc_logger',
    packages=find_packages(),
    install_requires=[
        'logstash_formatter',
    ],
    tests_require=['pytest'],
    dependency_links=[
        #'git+https://github.com/shokunin/python-logstash-formatter.git#egg=logstash_formatter',
        'git+https://github.com/shokunin/python-logstash-formatter.git@3c3d218226#egg=logstash_formatter',
    ],
    version = '0.0.1',
    description = 'General logging system to send events and stats the Clearcare way',
    author='Brian Zambrano',
    author_email='brianz@clearcareonline.com',
    url='https://github.com/clearcare/cc_logger',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: System :: Distributed Computing',
    ]
)
