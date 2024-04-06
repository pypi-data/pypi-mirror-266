import gluepy
import setuptools

requirements_base = open("./requirements/base.txt").read().split("\n")
requirements_all = open("./requirements/all.txt").read().split("\n")
requirements_dev = open("./requirements/dev.txt").read().split("\n")
requirements_digitalocean = open("./requirements/digitalocean.txt").read().split("\n")
requirements_gcp = open("./requirements/gcp.txt").read().split("\n")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gluepy",
    version=gluepy.VERSION,
    author="Marcus Lind",
    author_email="marcuslind90@gmail.com",
    description="A framework for data scientists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gluepy/gluepy",
    packages=setuptools.find_packages(),
    scripts=["gluepy/bin/gluepy-cli.py"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=(requirements_base + requirements_digitalocean),
    extra_require={
        "all": (requirements_base + requirements_dev + requirements_digitalocean),
        "digitalocean": (requirements_base + requirements_digitalocean),
        "gcp": (requirements_base + requirements_gcp),
    },
    entry_points="""
        [console_scripts]
        gluepy-cli=gluepy.commands.gluepy:cli
    """,
)
