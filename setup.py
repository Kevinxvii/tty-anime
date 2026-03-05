from setuptools import setup

setup(
    name="canime",
    version="1.0.0",
    description="CLI per lo streaming di anime da AnimeWorld",
    author="IlTuoNome",
    py_modules=["canime"],
    install_requires=[
        "animeworld",
        "requests",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "canime=canime:main",
        ],
    },
)