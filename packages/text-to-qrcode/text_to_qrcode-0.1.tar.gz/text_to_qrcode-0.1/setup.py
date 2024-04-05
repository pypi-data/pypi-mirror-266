
from setuptools import setup, find_packages

setup(
    name='text_to_qrcode',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'text_to_qrcode = text_to_qrcode.text_to_qrcode:main'
        ]
    },
    author='Sajal Sisodia',
    author_email='Sajal89304@gmail.com',
    description='A package for calculating factorial.',
    url='https://github.com/Sam-Sisodia/text_to_qQrocde.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "qrcode",
    ]
)
