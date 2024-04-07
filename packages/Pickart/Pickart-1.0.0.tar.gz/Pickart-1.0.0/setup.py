from setuptools import setup, find_packages

with open("LICENSE", "r", encoding="utf-8") as file:
    LICENSE = file.read()

with open("README.md", "r", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()

setup(
    name="Pickart",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    description="This is helper package for game called 'Colouring art'",
    author="AntynK",
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=["pygame>=2.1.2"],
    url="https://github.com/AntynK/Pickart"
)
