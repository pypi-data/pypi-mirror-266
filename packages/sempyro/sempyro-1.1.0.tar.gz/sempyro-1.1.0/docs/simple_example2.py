import dateutil.parser as parser
import pandas as pd
from sempyro import LiteralField
from sempyro.dcat import DCATDataset, DCATCatalog
from sempyro.vcard import VCard
from sempyro.foaf import Agent
from rdflib import URIRef, Graph
from typing import List

EX = "http://example.com"


def read_and_prepare_csv() -> pd.DataFrame:
    df = pd.read_csv("./example_data2.csv", sep=";")
    df["keywords"] = df["keywords"].apply(lambda x: x.split(","))
    df["theme"] = df["theme"].apply(lambda x: x.split(","))
    df["id"] = df["id"].apply(lambda x: [str(x)])
    # df["issued"] = pd.to_datetime(df["issued"], dayfirst=True)
    df["creator"] = df.apply(lambda x: [VCard(full_name=[x["author_name"]], hasUID=x["author_id"])], axis=1)
    df["publisher"] = df.apply(lambda x: Agent(name=[x["publisher_name"]], identifier=x["publisher_id"]), axis=1)
    df["contact_point"] = df.apply(lambda x: VCard(hasEmail=x["contact_point"], full_name=[x["author_name"]], 
                                                   hasUID=x["author_id"]), axis=1)
    return df


def create_catalog() -> DCATCatalog:
    catalog = DCATCatalog(title=[LiteralField(value="Student research works 1992")],
                          description=[LiteralField(value="Research works of 2nd grade Hogwarts students")],
                          identifier=[f"{EX}/catalog/1"],
                          release_date="01-06-1992",
                          dataset=[]
                          )
    return catalog


def convert_to_datasets(df) -> List[DCATDataset]:
    datasets = df.to_dict('records')
    dataset_objects = []
    for record in datasets:
        dataset = DCATDataset(
            title=[LiteralField(value=record["name"])],
            description=[LiteralField(value=record["description"])],
            identifier=record["id"],
            creator=record["creator"],
            release_date=record["issued"],
            publisher=[record["publisher"]],
            theme=record["theme"],
            keyword=[LiteralField(value=x) for x in record["keywords"]]
        )
        dataset_objects.append(dataset)
    return dataset_objects


def _combine_and_serialize(catalog: DCATCatalog, datasets: List[DCATDataset]) -> Graph:
    datasets_subjects = [URIRef(f"{EX}/dataset/{x.identifier[0]}") for x in datasets]
    catalog.dataset = datasets_subjects
    graph = catalog.to_graph(subject=URIRef(catalog.identifier[0]))
    for ds in datasets:
        ds_graph = ds.to_graph(URIRef(f"{EX}/dataset/{ds.identifier[0]}"))
        graph += ds_graph
    return graph


def csv_to_rdf(file_path):
    catalog = create_catalog()
    df = read_and_prepare_csv()
    datasets = convert_to_datasets(df)
    graph = _combine_and_serialize(catalog, datasets)
    graph.serialize(destination=file_path, format="ttl")


if __name__ == "__main__":
    csv_to_rdf("./example_rdf_2.ttl")
