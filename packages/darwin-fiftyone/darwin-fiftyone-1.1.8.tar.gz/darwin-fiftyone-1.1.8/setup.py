from setuptools import setup, find_packages

setup(
    name="darwin-fiftyone",
    version="1.1.8",
    description="Integration between V7 Darwin and Voxel51",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Simon Edwardsson & Mark Cox-Smith",
    packages=find_packages(),
    url="https://github.com/v7labs/darwin_fiftyone",
    install_requires=[
        "darwin-py",
        "fiftyone"
    ],
)
