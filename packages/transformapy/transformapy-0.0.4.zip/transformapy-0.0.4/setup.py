import setuptools

def readme_file():
    with open('README.rst') as rf:
        return rf.read()

setuptools.setup(
    name = 'transformapy',
    version = '0.0.4',
    author = 'Wang Rui',
    author_email = 'wtrt7009@gmail.com',
    url = 'https://github.com/WangRui5/TransformaPy',
    description = 'A Toolkit for Identifying Transformation Product Structures of Emerging Contaminants Using HRMS Data',
    long_description = readme_file(),
    packages = setuptools.find_packages(),
    install_requires = [],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

)
