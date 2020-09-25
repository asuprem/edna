from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="edna",

    install_requires=[
        "pyyaml>=5.3.1"
        "requests2>=2.16.0",
        "confluent-kafka>=1.5"
    ],

)