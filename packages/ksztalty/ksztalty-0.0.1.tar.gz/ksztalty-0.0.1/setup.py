import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ksztalty",
    version="0.0.1",
    author="Damian Tomczyszyn",
    author_email="damitom@o2.pl",
    description="Wyswietlanie printem ksztaltow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/damiantomczyszyn/Displayer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ]
)
