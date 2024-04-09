import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vloc",
    version="0.1.11",
    author="Lin Yeh",
    author_email="lin_yeh@outlook.com",
    description="An UI antomation tool based by YOLO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linyeh1129/vloc_plugin_selenium",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
    ],
    python_requires='>=3.10',
)
