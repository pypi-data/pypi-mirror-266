from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()
setup(
    name="uf-toolkit",
    version="0.2.2",
    packages=find_packages('uf-toolkit'),
    description="A simple Union Find Class for Python.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Chas Huggins",
    author_email="hugginsc10@gmail.com",
    url="https://github.com/hugginsc10/uf-toolkit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
)
