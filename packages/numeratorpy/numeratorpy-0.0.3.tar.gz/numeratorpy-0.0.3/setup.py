import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("numerator/version.py", "r") as version_file:
    exec(version_file.read())

setuptools.setup(
    name="numeratorpy",
    version=__version__,
    author="Amos Zhang",
    description="Python SDK for Numerator Feature Management Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "certifi==2024.2.2",
        "charset-normalizer==3.3.2",
        "idna==3.6",
        "requests==2.31.0",
        "urllib3==2.2.1",
    ]
)
