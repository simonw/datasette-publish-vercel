from setuptools import setup
import os

VERSION = "0.12.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-publish-vercel",
    description="Datasette plugin for publishing data using Vercel",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-publish-vercel",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-publish-vercel/issues",
        "CI": "https://github.com/simonw/datasette-publish-vercel/actions",
        "Changelog": "https://github.com/simonw/datasette-publish-vercel/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_publish_vercel"],
    entry_points={"datasette": ["publish_vercel = datasette_publish_vercel"]},
    install_requires=["datasette>=0.59"],
    extras_require={"test": ["pytest"]},
    tests_require=["datasette-publish-vercel[test]"],
)
