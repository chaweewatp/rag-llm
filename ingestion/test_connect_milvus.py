from dotenv import load_dotenv
import os
from pymilvus import connections, DataType
from pymilvus import has_collection, drop_collection

# from function import get_model, manage_collection

load_dotenv()
milvus_host = os.getenv("MILVUS_HOST", None)
milvus_port = os.getenv("MILVUS_PORT", None)
server_name = os.getenv("MILVUS_SERVER_NAME", None)
user_name = os.getenv("MILVUS_USERNAME", None)
password = os.getenv("MILVUS_PASSWORD", None)
collection_name = os.getenv("MILVUS_COLLECTION_NAME", None)
milvus_host = "172.20.10.3"
milvus_port = "19530"
connections.connect("default", host=milvus_host, port=milvus_port)

if has_collection(collection_name):
    print("drop collection")
    drop_collection(collection_name)

