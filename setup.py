from setuptools import setup
import os

VERSION = "0.1a"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-publish-now",
    description="Datasette plugin for publishing data using Zeit Now",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-publish-now",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_publish_now"],
    entry_points={"datasette": ["publish_now = datasette_publish_now"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest"]},
    tests_require=["datasette-publish-now[test]"],
)
