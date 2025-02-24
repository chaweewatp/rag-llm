from dotenv import load_dotenv
import os
from pymilvus import connections, DataType
from pymilvus import has_collection, drop_collection

from function import get_model, manage_collection
import pandas as pd

load_dotenv()
milvus_host = os.getenv("MILVUS_HOST", None)
milvus_port = os.getenv("MILVUS_PORT", None)
server_name = os.getenv("MILVUS_SERVER_NAME", None)
user_name = os.getenv("MILVUS_USERNAME", None)
password = os.getenv("MILVUS_PASSWORD", None)
collection_name = os.getenv("MILVUS_COLLECTION_NAME", None)


data_dictionary1 = pd.read_csv("./data/sample_Comply_reg0036_พ.ร.บ.ความปลอดภัย พ.ศ.2554.csv")
data_dictionary = pd.concat([data_dictionary1], axis=0)
data_dictionary= data_dictionary.reset_index()


data_dictionary["text_to_encode"] = [
    f"Regulation number: {RegNumber}\nRegulation title:{RegTitle}\nSection number:{SectionNumber}\nSecion detail:{SectionDetail}"
    for RegNumber, RegTitle, SectionNumber, SectionDetail in zip(data_dictionary["RegNumber"], data_dictionary["RegTitle"], data_dictionary["SectionNumber"], data_dictionary["SectionDetail"])
]


text_to_encode_list = data_dictionary["text_to_encode"].tolist()
regulation_title_list = data_dictionary["RegTitle"].tolist()
section_number_list = data_dictionary["SectionNumber"].tolist()
section_detail_list = data_dictionary["SectionDetail"].tolist()

model = get_model(model_name='kornwtp/simcse-model-wangchanberta', max_seq_length=768)

embeds = []
for index, text in enumerate(data_dictionary["text_to_encode"]):
    try:
        embed = model.encode(text)
        embeds.append(list(embed))
    except RuntimeError as e:
        print(f"Error with text at index {index}: {text}")
        print(e)
        break



connections.connect("default", host=milvus_host, port=milvus_port, server_name=server_name)

if has_collection(collection_name):
    drop_collection(collection_name)

schema = {
    "embeddings": DataType.FLOAT_VECTOR, 
    "text_to_encode": DataType.VARCHAR, 
    "RegTitle": DataType.VARCHAR,
    "SectionNumber": DataType.VARCHAR, 
    "SectionDetail": DataType.VARCHAR,
}


collection = manage_collection(collection_name, schema, ID_MAX_LENGTH=50000, EMBEDDINGS_DIMENSION=768, TEXT_MAX_LENGTH=50000)
print("initialized new collection")
collection.insert([embeds, text_to_encode_list, regulation_title_list, section_number_list, section_detail_list])


collection.create_index(field_name="embeddings",\
                        index_params={"metric_type":"IP","index_type":"IVF_FLAT","params":{"nlist":16384}})

print("ingesting into Milvus - completed")

