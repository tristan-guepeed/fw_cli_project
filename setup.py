from setuptools import setup, find_packages

setup(
    name="fastwizard",
    version="0.1.0",
    packages=find_packages(),  # inclut fastwizard/
    install_requires=[
        "typer",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "fastwizard=fastwizard.cli:main",  # <-- référence l'application Typer
        ],
    },
    python_requires=">=3.10",
    description="Un générateur de projets FastAPI modulaire et interactif",
    author="T.B",
)
