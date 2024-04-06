from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='NitroPy',
    version='1.2.1',
    author='Malakai',
    author_email='Almightyslider2@gmail.com',
    description='A package for interacting with the website, Nitrotype and Nitromath',

    long_description=long_description,
    long_description_content_type='text/markdown',
    #    url='https://github.com/yourusername/nitrotype-package',
    packages=[
        "nitrotype"
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    python_requires='>=3.6',
    install_requires=[
        'cloudscraper',
        'beautifulsoup4',
        'twine'
    ],
)
