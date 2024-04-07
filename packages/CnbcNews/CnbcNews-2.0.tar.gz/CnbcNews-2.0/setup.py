from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='CnbcNews',
    version='2.0',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'pandas'
    ],
    entry_points={
        "console_scripts": [
            "CnbcNews-getArticles = CnbcNews.main:main",
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
)