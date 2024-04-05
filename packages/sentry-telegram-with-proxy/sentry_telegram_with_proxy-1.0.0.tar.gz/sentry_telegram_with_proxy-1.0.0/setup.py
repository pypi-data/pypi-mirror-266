#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

from sentry_telegram_with_proxy import __version__



setup(
    name='sentry_telegram_with_proxy',
    version=__version__,
    packages=['sentry_telegram_with_proxy'],
    url='https://github.com/ivantzepner/sentry-telegram',
    author='Ivan Tzepner',
    author_email='ivan.tzepner@gmail.com',
    description='Plugin for Sentry which allows sending notification via Telegram messenger.',
    long_description_content_type='text/x-rst',
    license='MIT',
    entry_points={
        'sentry.plugins': [
            'sentry_telegram_with_proxy = sentry_telegram_with_proxy.plugin:TelegramNotificationsPlugin',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Monitoring',
    ],
    include_package_data=True,
)
