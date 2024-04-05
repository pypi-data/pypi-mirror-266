from setuptools import find_packages, setup

setup(
    name="prl-cli",
    version="0.0.30",
    author="Langston Nashold, Rayan Krishnan",
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["jsonschemas/*"]},
    install_requires=[
        "Click",
        "gql",
        "attrs",
        "jsonschema",
        "tqdm",
        "boto3",
        "requests",
        "aiohttp",
        "pandas",
        "requests-toolbelt",
    ],
    entry_points={
        "console_scripts": [
            "prl = prl.cli.main:cli",
        ],
    },
    url="http://pypi.python.org/pypi/prl-cli/",
)
