import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="ipaddress-finder-dsa",
    version="0.0.1",
    author="Saeed Adetugboboh",
    author_email="dadetugboboh1@gmail.com",
    description="A package that allows you to get ip address, as well as country, city and region",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=[''],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)