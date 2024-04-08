from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='FNews',
    version='1.2',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pandas',
    ],
    entry_points={
        "console_scripts": [
            "FNews-getArticles = FNews.main:main",
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
)