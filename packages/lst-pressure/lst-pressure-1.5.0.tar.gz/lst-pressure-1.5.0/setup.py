from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
        return long_description


setup(
    name="lst-pressure",
    setup_requires=["katversion"],
    use_katversion=True,
    description='Determine periods of "LST pressure" by querying for intersections between LST/Solar intervals',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/ska-sa/lst-pressure",
    author="Zach Smith",
    author_email="zsmith@sarao.ac.za",
    license="Apache 2.0",
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={},
    packages=find_packages(where="./"),
    python_requires=">=3.12",
)
