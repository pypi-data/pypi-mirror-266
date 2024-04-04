from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='PyFaceCrop',
    version='0.0.4',
    packages=find_packages(),
    install_requires=['opencv-python'],
    long_description = description,
    long_description_content_type = "text/markdown"
)


