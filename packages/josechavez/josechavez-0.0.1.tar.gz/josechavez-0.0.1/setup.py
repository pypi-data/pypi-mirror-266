import setuptools
from pathlib import Path
readme = Path("README.md").read_text(encoding="utf8")
setuptools.setup(
    name="josechavez",
    author="Emmanuel Chavez",
    version="0.0.1",
    author_email="jechmx1@gmail.com",
    long_description=readme,
    packages=setuptools.find_packages(
        exclude=["mocks", "tests"]
    )
)
