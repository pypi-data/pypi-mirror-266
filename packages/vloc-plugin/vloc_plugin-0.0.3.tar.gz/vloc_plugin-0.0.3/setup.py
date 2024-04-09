import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vloc_plugin",
    version="0.0.2",
    author="Lin Yeh",
    author_email="lin_yeh@outlook.com",
    description="Plugin functions for vloc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linyeh1129/vloc_plugin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
    ],
    python_requires='>=3.10',
)
