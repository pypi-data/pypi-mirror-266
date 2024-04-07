from setuptools import setup


REQUIREMENTS_FILENAME = "requirements.txt"
REQUIREMENTS_TEST_FILENAME = "requirements_test.txt"
REQUIREMENTS_DOCS_FILENAME = "requirements_docs.txt"


# Requirements
try:
    with open(REQUIREMENTS_FILENAME, encoding="utf-8") as fh:
        REQUIRED = fh.read().split("\n")
except FileNotFoundError:
    REQUIRED = []

try:
    with open(REQUIREMENTS_TEST_FILENAME, encoding="utf-8") as fh:
        TEST_REQUIRED = fh.read().split("\n")
except FileNotFoundError:
    TEST_REQUIRED = []

try:
    with open(REQUIREMENTS_DOCS_FILENAME, encoding="utf-8") as fh:
        DOCS_REQUIRED = fh.read().split("\n")
except FileNotFoundError:
    DOCS_REQUIRED = []

# What packages are optional?
EXTRAS = {
    "test": TEST_REQUIRED,
    "docs": DOCS_REQUIRED,
}


setup(
    install_requires=REQUIRED,
    extras_require=EXTRAS,
)
