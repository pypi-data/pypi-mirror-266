from setuptools import setup, find_packages

setup(
    name='CnbcNews',
    version='1.6',
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
)