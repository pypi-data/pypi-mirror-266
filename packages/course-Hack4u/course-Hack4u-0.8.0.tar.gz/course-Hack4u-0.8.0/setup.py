from setuptools import setup, find_packages

# Leer el contenido del archivo README.md
with open("REAMD.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="course-Hack4u",
    version="0.8.0",
    packages=find_packages(),
    install_requires=[],
    author="Arc4he",
    description="Bibliotecas de los cursos actuales de hack4u",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
)