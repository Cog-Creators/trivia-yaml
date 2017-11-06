from setuptools import setup

with open("requirements.txt") as file:
    requirements = file.readlines()

with open("README.rst") as file:
    readme = file.read()

setup(
    name="trivia-yaml",
    author="Tobotimus",
    description="Convert Red's V2 trivia lists to YAML",
    long_description=readme,
    version="0.0.1",
    license="MIT",
    install_requires=requirements,
    py_modules=["triviayaml"],
    namespace_packages=[],
    include_package_data=True,
    entry_points={"console_scripts": ["trivia-yaml=triviayaml:main"]}
)
