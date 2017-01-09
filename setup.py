from setuptools import find_packages
from setuptools import setup

REQUIREMENTS = [
    'python-lua-ast == 0.0.4',
]

DEPENDENCY_LINKS = [
    'https://github.com/paluh/python-lua-ast/archive/0.0.4.zip#egg=python-lua-ast-0.0.4'
]

setup(
    name = "python-prosody-config",
    version = "0.0.1",
    author = "Tomasz Rybarczyk",
    author_email = "paluho@gmail.com",
    description = ("Prosody configuration file editor"),
    dependency_links=DEPENDENCY_LINKS,
    license = "BSD",
    keywords = "prosody configuration xmpp",
    scripts=[],
    packages=find_packages(exclude=['tests']),
    install_requires=REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
