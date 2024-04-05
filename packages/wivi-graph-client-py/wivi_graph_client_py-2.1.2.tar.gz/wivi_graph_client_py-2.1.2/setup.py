from setuptools import setup, find_packages

setup(
    name="wivi_graph_client_py",
version="2.1.2",
    packages=find_packages(),
    install_requires=[
        "requests",
        "graphql-core",
    ],
    author="Haseeb Saif Ullah",
    author_email="hsaif@intrepidcs.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
