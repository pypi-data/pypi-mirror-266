from sempyro.dcat import DCATDataset
import pprint

# dcat_fields = DCATDataset.annotate_model()
# pprint(dcat_fields.fields_description())
# 
# from sempyro.dcat import DCATDataset
# import pprint

from tabulate import tabulate
import pandas as pd

df = pd.read_csv("./example_data.csv", sep=";")

from sempyro.vcard import VCard

df["keywords"] = df["keywords"].apply(lambda x: x.split(","))
df["id"] = df["id"].apply(lambda x: [str(x)])
df["creator"] = df.apply(lambda x: {"full_name": [x["author_name"]], "hasUID": x["author_id"]}, axis=1)
df.drop(columns=["author_name", "author_id"], inplace=True)
df.rename(columns={"id": "identifier", "name": "title", "keywords": "keyword"}, inplace=True)
                                                       
datasets = df.to_dict('records')
print()