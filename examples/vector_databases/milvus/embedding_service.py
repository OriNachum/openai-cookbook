# Import required libraries
import os
from pymilvus import DataType, connections, utility, FieldSchema, Collection, CollectionSchema
import openai
from scripts.complete_prompt import complete_prompt
from scripts.create_embedding import create_embedding

class EmbeddingService:
    def __init__(self, collection_name):
        # Initialize Milvus client
        connections.connect(alias='default', host='localhost', port='19530')
        
        # Collection (database) name
        self.collection_name = collection_name

        # Check if collection exists, if not create one
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='title', dtype=DataType.VARCHAR, max_length=64000),
                FieldSchema(name='description', dtype=DataType.VARCHAR, max_length=64000),
                FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=1536)
            ]
            schema = CollectionSchema(fields=fields, description="Book Collection", auto_id=True)
            self.collection = Collection(name=self.collection_name, schema=schema, using='default')

            # Create the index on the collection and load it.
            index_param = {
                'metric_type': 'L2',
                'index_type': 'HNSW',
                'params': {'M': 8, 'efConstruction': 64}
            }
            self.collection.create_index("embedding", index_param)
            self.collection.load()

    def generate_embeddings(self, text):
        # Pre-phrase the text
        text = self.pre_phrase(text)
        
        # Generate embeddings using OpenAI
        embeddings = create_embedding(text)
        
        return embeddings

    def pre_phrase(self, text):
        # Define a system prompt for pre-phrasing
        prompt = "Assume the role of a data scientist expert in text rephrasing, geared towards optimizing embedding generation for a vector database. You will receive snippets from conversations or FAQs. Your task is to rephrase the sentences, emphasizing the most crucial information. Strive to phrase the content such that it retains vital information while minimizing noise."
        
        # Pre-phrase the text
        text = complete_prompt(text, prompt, "gpt-3.5-turbo", 0.05)
        
        return text

    def insert_records(self, records):
        # Generate embeddings for all records
        embeddings = [self.generate_embeddings(record["description"]) for record in records]
        titles = [record["title"] for record in records]
        descriptions = [record["description"] for record in records]
        
        # Insert records into Milvus
        self.collection.insert({"title": titles, "description": descriptions, "embedding": embeddings}, using='default')

    def search_records(self, query, top_k):
        # Generate embeddings for the query
        query_embeddings = self.generate_embeddings(query)
        
        # Search for similar records in Milvus
        results = self.collection.search({"embedding": query_embeddings}, top_k=top_k, output_fields=['title', 'description'], using='default')
        
        return results
