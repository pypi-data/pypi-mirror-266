from setuptools import setup, find_packages

# Leer el contenido del archivo Readme.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Hack4u-Allen",
    version="0.5.13",
    packages=find_packages(),
    install_requires=[],
    author="Marcelo Vásquez",
    description="Una biblioteca para consultar tus cursos de hack4u",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
)
