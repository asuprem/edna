from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
requires = [
        "msgpack>=1.0.0",
        "pyyaml>=5.3.1",
        "requests2>=2.16.0",
        "confluent-kafka>=1.5",
        "ujson>=3.2.0"
    ]

recommended = {
    "mysql": ["mysql-connector-python>=8.0.21"],
    "sklearn":["scikit-learn>=0.23.2"]
}
# Create full install that includes all extra dependencies
full = []
for extra_dependency_category in recommended:
    full+=recommended[extra_dependency_category]
full = list(set(full))
recommended["full"] = full
setup(
    name="edna",
    install_requires=requires,
    extras_require = recommended

)