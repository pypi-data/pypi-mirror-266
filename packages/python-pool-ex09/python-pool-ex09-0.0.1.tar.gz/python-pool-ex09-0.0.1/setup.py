import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="python-pool-ex09",
    version="0.0.1",
    author="ytouate",
    description="Python for datascience bootcamp exercice number 9",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ytouate/1337-PYTHON-POOL",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
