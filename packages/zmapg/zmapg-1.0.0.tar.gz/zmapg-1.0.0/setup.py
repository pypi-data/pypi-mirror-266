from setuptools import setup, find_packages

setup(
    name='zmapg',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'tk',
        'ttkthemes',
    ],
    entry_points={
        'console_scripts': [
            'zmapg=zmapg.app:main',
        ],
    },
    author='atiilla',
    description='ZMap GUI application for zmap-cli tool',
    license='MIT',
    keywords='zmap ui tkinter',
    url='https://github.com/atiilla/zmapg',
)
