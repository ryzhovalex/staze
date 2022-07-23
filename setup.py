from setuptools import setup, find_packages

from staze import __version__ as version


with open("requirements.txt", "r") as file:
    install_requires = [x.strip() for x in file.readlines()]

setup(
    name="staze",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="Upgraded layer over Flask.",
    author="Alexander Ryzhov",
    author_email="thed4rkof@gmail.com",
    url="https://github.com/ryzhovalex/staze",
    keywords=["flask+", "web-framework", "flask", "flask-template"],
    entry_points={
        "console_scripts": [
            "staze = staze.core.cli.cli:main",
        ],
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.10",
    ],
)
