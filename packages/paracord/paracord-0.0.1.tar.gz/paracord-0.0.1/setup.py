from setuptools import find_packages, setup

setup(
    name="paracord",
    description="Coming soon.",
    author="Justin Mitchel",
    author_email="getparacord@gmail.com",
    url="https://github.com/getparacord/paracord",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["paracord=paracord.__main__:main"]},
    install_requires=[
        "fire",
        "PyYAML",
        "rich",
    ],
    python_requires=">=3.11",
)
