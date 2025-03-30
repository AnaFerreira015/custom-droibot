from setuptools import setup, find_packages, findall
import os

setup(
    name='droidbot',
    packages=find_packages(include=['droidbot', 'droidbot.*']),
    version='1.0.2b4',
    description='A lightweight UI-guided test input generator for Android.',
    author='Yuanchun Li',
    license='MIT',
    author_email='pkulyc@gmail.com',
    url='https://github.com/honeynet/droidbot',
    download_url='https://github.com/honeynet/droidbot/tarball/1.0.2b4',
    keywords=['testing', 'monkey', 'exerciser'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'droidbot=start:main',
        ],
    },
    package_data={
        'droidbot': [os.path.relpath(x, 'droidbot') for x in findall('droidbot/resources/')]
    },
    install_requires=[
        'androguard>=3.4.0a1',
        'networkx',
        'Pillow',
        'lxml',
        'uiautomator',
        'numpy',
        'opencv-python'
    ],
)
