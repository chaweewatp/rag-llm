# from dotenv import load_dotenv
from pymilvus import utility, Collection, CollectionSchema, FieldSchema, DataType
from sentence_transformers import SentenceTransformer, models

# load_dotenv()

def create_field_schema(schema, EMBEDDINGS_DIMENSION, TEXT_MAX_LENGTH):
    """Create field schemas for the collection."""
    final_schema = [FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)]
    for key in schema:
        if schema[key] == DataType.FLOAT_VECTOR:
            curr_schema = FieldSchema(name=key, dtype=schema[key], dim=EMBEDDINGS_DIMENSION)
        elif schema[key] == DataType.VARCHAR:
            curr_schema = FieldSchema(name=key, dtype=schema[key], max_length=TEXT_MAX_LENGTH)
        else:
            pass
        final_schema.append(curr_schema)
    return final_schema

def create_collection_schema(fields, description="Search promotional events"):
    """Create a collection schema with the provided fields."""
    return CollectionSchema(fields=fields, description=description, enable_dynamic_field=True)

def initialize_collection(collection_name, schema, using='default'):
    """Initialize a collection with the given name and schema."""
    return Collection(name=collection_name, schema=schema, using=using)

def manage_collection(collection_name, schema, ID_MAX_LENGTH=50000, EMBEDDINGS_DIMENSION=1024, TEXT_MAX_LENGTH=50000):
    """Manage the creation or replacement of a collection."""
    print("Existing collections:", utility.list_collections())
    if collection_name in utility.list_collections():
        utility.drop_collection(collection_name)
        print("Dropped old collection")

    # Ensure collection is dropped
    existing_collections = utility.list_collections()
    print(f"Existing collections after drop operation: {existing_collections}")

    fields = create_field_schema(schema, EMBEDDINGS_DIMENSION, TEXT_MAX_LENGTH)
    print("Fields for new collection:", fields)

    schema = create_collection_schema(fields)
    collection = initialize_collection(collection_name, schema)
    print(f"Initialized new collection: {collection_name}")
    return collection

def get_model(model_name='airesearch/wangchanberta-base-att-spm-uncased', max_seq_length=768, condition=True):
    if condition:
        word_embedding_model = models.Transformer(model_name, max_seq_length=max_seq_length)
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),pooling_mode='cls') # We use a [CLS] token as representation
        model = SentenceTransformer(modules=[word_embedding_model, pooling_model],cache_folder='./tmp')
    return model

