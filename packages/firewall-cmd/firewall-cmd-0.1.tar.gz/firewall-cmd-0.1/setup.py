from setuptools import find_packages, setup

setup(
    name="firewall-cmd",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.6",
    author="Shay Elmualem",
    author_email="shay@legitsecurity.com",
    description="A test package - please do not use right now",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shay-legit/firewall-cmd",
)
