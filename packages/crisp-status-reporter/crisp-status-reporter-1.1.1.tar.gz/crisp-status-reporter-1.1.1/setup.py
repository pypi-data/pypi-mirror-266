# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


setup(
    name='crisp-status-reporter',
    version='1.1.1',
    author=u'Valerian Saliou',
    author_email='valerian@valeriansaliou.name',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/crisp-im/python-crisp-status-reporter',
    license='MIT - http://opensource.org/licenses/mit-license.php',
    description='Crisp Status Reporter for Python.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
    ],
    install_requires=[],
    zip_safe=False,
)
