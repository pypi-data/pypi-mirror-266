from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PyGz1',
    version='0.4.0',
    description='A Python library for Internet interaction.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='MrGengar',
    author_email='rydikminecraft@gmail.com',
    packages=["pygz1"],  # Замените "your_package" на название вашей директории с пакетом
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='internet interaction requests',
)