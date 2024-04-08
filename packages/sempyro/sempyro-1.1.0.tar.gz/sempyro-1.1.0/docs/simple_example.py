import random
import string

from sempyro import LiteralField
from sempyro.dcat import DCATDataset, DCATCatalog
from rdflib import URIRef, Graph
# This script creates a random minimal DCAT-AP compatible rdf file

EX = "http://example.com"


def create_random_file(file_path):
    catalog = _create_random_catalog()
    catalog.dataset = []
    datasets = Graph()
    for i in range(2):
        identifier = "".join(random.choices(string.ascii_letters + string.digits, k=15)) + str(i)
        dataset = _create_random_dataset(identifier)
        datasets += dataset
        catalog.dataset.append(URIRef(f"{EX}/dataset_{identifier}"))
    catalog_subject = URIRef(f"{EX}/catalog_{catalog.identifier}")
    catalog_graph = catalog.to_graph(catalog_subject)
    result = catalog_graph + datasets
    result.serialize(destination=file_path, format="ttl")


def _create_random_catalog() -> DCATCatalog:
    identifier = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    title = f"Example calalog {identifier}"
    description = f"Example description for catalog {identifier}"
    catalog = DCATCatalog(
        title=[LiteralField(value=title, language="en")],
        description=[LiteralField(value=description)],
        identifier=[identifier]
    )
    return catalog


def _create_random_dataset(identifier: str) -> Graph:
    title = f"Example dataset {identifier}"
    description = f"Example description for dataset {identifier}"
    dataset = DCATDataset(
        title=[LiteralField(value=title, language="en")],
        description=[LiteralField(value=description)],
        identifier=[identifier]
    )
    dataset_subject = URIRef(f"{EX}/dataset_{identifier}")
    dataset_graph = dataset.to_graph(dataset_subject)
    return dataset_graph


if __name__ == "__main__":
    create_random_file("./example_rdf.ttl")
