import codecs
from os.path import abspath, dirname, join

from Cython.Build import cythonize
from setuptools import find_packages, setup


TEST_DEPS = ["coverage[toml]", "pytest", "pytest-cov"]
DOCS_DEPS = [
    "sphinx",
    "sphinx-rtd-theme",
    "sphinx-autoapi",
    "recommonmark",
    "sphinxcontrib-runcmd",
]
CHECK_DEPS = ["isort", "flake8", "flake8-quotes", "pep8-naming", "mypy", "black"]
REQUIREMENTS = ["lxml"]

EXTRAS = {
    "test": TEST_DEPS,
    "docs": DOCS_DEPS,
    "check": CHECK_DEPS,
    "dev": TEST_DEPS + DOCS_DEPS + CHECK_DEPS,
}

# Read in the version
with open(join(dirname(abspath(__file__)), "VERSION")) as version_file:
    version = version_file.read().strip()


setup(
    name="V8 Pak Dump",
    version=version,
    description="Dump the data from .pak files for GFDM V8",
    long_description=codecs.open("README.md", "r", "utf-8").read(),
    long_description_content_type="text/markdown",
    author="573dev",
    author_email="",
    url="https://github.com/573dev/pakdump",
    packages=find_packages(exclude=["tests"]),
    install_requires=REQUIREMENTS,
    ext_modules=cythonize(["cython-deps/pakdec.pyx"], annotate=True, language_level=3),
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    platforms=["any"],
    include_package_data=True,
    tests_require=TEST_DEPS,
    extras_require=EXTRAS,
    entry_points={
        "console_scripts": [
            "pakdump = pakdump.pakdump_base:main",
            "mdbdump = pakdump.mdbdump_base:main",
            "mdbcreate = pakdump.mdbcreate_base:main",
        ]
    },
)
