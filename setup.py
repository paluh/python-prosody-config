from setuptools import find_packages
from setuptools import setup

REQUIREMENTS = [
    'python-lua-ast == 0.0.2',
]

DEPENDENCY_LINKS = [
    'git+git://github.com/paluh/python-lua-ast.git@0.0.2#egg=python-lua-ast-0.0.2',
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
