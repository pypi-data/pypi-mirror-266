from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Operating System :: Microsoft :: Windows :: Windows 11",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3"
]

setup(
    name="downloadpy",
    version="0.0.1",
    description="Download Files from Internet",
    long_description=open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    url="",
    author="Linix Red",
    author_email="linixred@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="download",
    packages=find_packages(),
    install_requires=["requests"]
)