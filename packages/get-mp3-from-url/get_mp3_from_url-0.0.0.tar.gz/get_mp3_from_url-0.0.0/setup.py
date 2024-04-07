"""Setup of get_mp3_from_url."""

from setuptools import find_packages, setup

setup(
    name="get_mp3_from_url",
    version="0.0.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["get_mp3_from_url = get_mp3_from_url.main:main"]},
    author="Maxime Haselbauer",
    author_email="maxime.haselbauer@googlemail.com",
    description="A tool to download mp3 files from url",
    license="MIT",
    keywords="keywords ",
    url="https://github.com/renn0xtek9/get_mp3_from_url",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["ffmpeg", "yt_dlp"],
)
