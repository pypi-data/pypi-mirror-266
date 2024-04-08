from setuptools import setup, find_packages

setup(
    name="chesscli",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "chesscli=chesscli.main:app",
        ],
    },
    install_requires=[
        "typer",
        "subprocess.run", 
    ],
    python_requires='>=3.7',
    description="A CLI tool for managing chess game development environment.",
    author="Neel Patel",
)
