import setuptools

def readfile(filename):
    with open(filename, 'r', encoding='latin1') as f:
        return f.read()

setuptools.setup(    
    name="pybureaucrat",
    version=readfile('version.txt'),
    author="Erick Fernando Mora Ramirez",
    author_email="erickfernandomoraramirez@gmail.com",
    description="A python client for bureaucrat server",
    long_description=readfile('README.MD'),
    long_description_content_type="text/markdown",
    url="https://github.com/LostSavannah/bureaucrat/tree/main/lib",
    project_urls={
        "Bug Tracker": "https://dev.moradev.dev/pybureaucrat/issues",
        "Documentation": "https://dev.moradev.dev/pybureaucrat/documentation",
        "Examples": "https://dev.moradev.dev/pybureaucrat/examples",
    },
    package_data={
        "":["*.txt"]
    },
    classifiers=[
    "Programming Language :: Python :: 3",
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    ],
    package_dir={"": "client"},
    packages=setuptools.find_packages(where="client"),
    python_requires=">=3.6"
)