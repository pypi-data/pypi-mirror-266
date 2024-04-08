from setuptools import setup, find_packages

with open("readme.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
setup(
    name="slash_path",
    version="0.1.1",
    author="Nutalk",
    author_email="ht2005112@hotmail.com",
    description="use windows path to generate Path object.",
    license="BSD",
    keywords="path",
    url="https://github.com/nutalk/slash_path",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)