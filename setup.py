from setuptools import setup, find_packages

setup(
    name="gibbon_flow",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "flow_gibbon = gibbon_flow.flow_gibbon:main",
        ],
    },
    install_requires=[
        'PyYAML',
        'croniter',
        'schedule',
        'dask[distributed]',
    ],
)