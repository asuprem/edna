from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="ebka",

    install_requires=[
        "requests2>=2.16.0",
        "confluent-kafka>=1.5"
    ],

)