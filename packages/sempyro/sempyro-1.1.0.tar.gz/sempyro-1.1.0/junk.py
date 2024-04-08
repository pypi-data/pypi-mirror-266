# file = "../__tests__/test_data/spatial_ex29.ttl"
# 
# g = Graph().parse(file)

print()
#[o for o in g.objects()][3].datatype = URIRef(http://www.opengis.net/ont/geosparql#wktLiteral)

from sempyro.dcat.dcat_dataset import DCATDataset
from sempyro import LiteralField
from rdflib import XSD, URIRef

model_fields = DCATDataset.annotate_model()
m = model_fields.get_fields_types()



dataset_title = LiteralField(value="Test dataset title", language="en")
dataset_title_nl = LiteralField(value="Titel van de testdataset", language="nl")
description = LiteralField(value="This is description of Test dataset", language="en")
version = LiteralField(value="1.0", datatype="xsd:string")
identifier = LiteralField(value="ts1234", datatype=XSD.string)

dataset = DCATDataset(title=[dataset_title, dataset_title_nl],
                      description=[description],
                      version=[version],
                      identifier=[identifier]
                      )
print(dataset.to_graph(URIRef("http://example.com/test_dataset")).serialize())

# import erdantic as erd
# from sempyro.dcat import DCATCatalog, DCATDistribution, DCATResource, DatasetSeries, DataService, DCATDataset
# from sempyro.time import PeriodOfTime, TimeInstant, TimePosition, GeneralDateTimeDescription
# from sempyro.hri_dcat import HRIDataset, HRICatalog, HRIDistribution, HRIDataService
# 
# # Easy one-liner
# erd.draw(HRIDataService, out="hri_dataservice.png")

# # Or create a diagram object that you can inspect and do stuff with
# diagram = erd.create(DCATResource)
# diagram.models
# #> [PydanticModel(Adventurer), PydanticModel(Party), PydanticModel(Quest), PydanticModel(QuestGiver)]
# diagram.draw("resource.png")

text = """
# Copyright 2024 Stichting Health-RI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
import os
from pathlib import Path

for root, dirs, files in os.walk("./models/hri_dcat"):
    for file in files:
        if file.startswith("hri_"):
            new_file_name = file + ".license"
            with open(Path(root, new_file_name), "w") as f:
                f.write(text)
    