#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='telegram_collector',
    version='0.1.0',
    author='fengleicn',
    author_email='fengleisemail@gmail.com',
    url='https://github.com/fengleicn/telegram_collector',
    description=u'收集电报群组的视频图片消息',
    packages=['telegram_collector'],
    install_requires=['telethon', 'python_socks'],
    entry_points={
        'console_scripts': [
            'tgc=telegram_collector.__main__:main'
        ]
    }
)
