import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # Here is the module name.
    name="synch2jira",
    # version of the module
    version="0.0.167",
    # Name of Author
    author="wefine",
    # your Email address
    author_email="wefine2529@ebuthor.com",
    # #Small Description about module
    description="Lib",

    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),

    install_requires=[
        "requests==2.31.0",
        "setuptools==68.2.0",
        "SQLAlchemy==2.0.25"
    ],

    license="MIT",
    # classifiers like program is suitable for python3, just leave as it is.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
