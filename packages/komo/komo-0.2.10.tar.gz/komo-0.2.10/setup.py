"""
Komodo AI CLI
"""

from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    dependencies = f.readlines()

setup(
    name="komo",
    version="0.2.10",
    url="https://github.com/anishchopra/komo",
    license="BSD",
    author="Anish Chopra",
    author_email="anish@komodoai.dev",
    description="Komodo AI CLI",
    long_description=__doc__,
    packages=find_packages(exclude=["tests", "komoproj.yaml"], include=["*"]),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=dependencies,
    entry_points={
        "console_scripts": [
            "komo = komo.cli.cli:cli",
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
