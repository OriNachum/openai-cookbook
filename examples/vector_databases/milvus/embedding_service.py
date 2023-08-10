# Import required libraries
import os
from pymilvus import DataType, connections, utility, FieldSchema, Collection, CollectionSchema
import openai
from scripts.complete_prompt import complete_prompt
from scripts.create_embedding import create_embedding

class EmbeddingService:
    def _initialize_embedding_collection(self, collection_name, description):
        return self._initialize_collection(
            collection_name,
            fields=[
                FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=1536),
                FieldSchema(name='entity_id', dtype=DataType.INT64)
            ],
            description=description,
            auto_id=True
        )

    def __init__(self, entities_collection_name, answer_embedding_collection_name, question_embedding_collection_name, full_embedding_collection_name):
        # Initialize Milvus client
        connections.connect(alias='default', host='localhost', port='19530')

        # Define Collection Names
        self.entities_collection_name = entities_collection_name
        self.answer_embedding_collection_name = answer_embedding_collection_name
        self.question_embedding_collection_name = question_embedding_collection_name
        self.full_embedding_collection_name = full_embedding_collection_name

        # Initialize Entities Collection
        self.entities_collection = self._initialize_collection(
            self.entities_collection_name,
            fields=[
                FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='owner', dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name='question', dtype=DataType.VARCHAR, max_length=64000),
                FieldSchema(name='answer', dtype=DataType.VARCHAR, max_length=64000)
            ],
            description="Entities Collection",
            auto_id=True
        )

        # Initialize Answer Embedding Collection
        self.answer_embedding_collection = self._initialize_embedding_collection(
            self.answer_embedding_collection_name, "Answer Embedding Collection")

        # Initialize Question Embedding Collection
        self.question_embedding_collection = self._initialize_embedding_collection(
            self.question_embedding_collection_name, "Question Embedding Collection")

        # Initialize Full Embedding Collection
        self.full_embedding_collection = self._initialize_embedding_collection(
            self.full_embedding_collection_name, "Full Embedding Collection")


    def _initialize_collection(self, collection_name, fields, description, auto_id):
        # Check if collection exists, if not create one
        if not utility.has_collection(collection_name):
            schema = CollectionSchema(fields=fields, description=description, auto_id=auto_id)
            collection = Collection(name=collection_name, schema=schema, using='default')
            # Create the index on the collection and load it
            index_param = {
                'metric_type': 'L2',
                'index_type': 'HNSW',
                'params': {'M': 8, 'efConstruction': 64}
            }
            collection.create_index("embedding", index_param)
            collection.load()
        else:
            # If the collection already exists, just load it
            collection = Collection(name=collection_name)
            collection.load()
        return collection

    def pre_phrase(self, text):
        # Define a system prompt for pre-phrasing
        prompt = "As a data scientist specializing in text rephrasing for embedding generation, you are tasked with processing snippets from conversations or FAQs. Your goal is to rephrase these sentences to highlight the most critical information. Aim for a rephrase that maintains essential details while minimizing irrelevant noise. Remember, the ultimate goal is to optimize these phrases for embedding generation within a vector database."

        # Pre-phrase the text
        text = complete_prompt(text, prompt, "gpt-3.5-turbo", 0.05)
        return text

    def insert_records(self, records):
        # Insert entities
        entity_ids = self._insert_entities(records)

        # Insert Embeddings
        self._insert_embeddings(records, entity_ids, self.question_embedding_collection, lambda record: record["question"])
        self._insert_embeddings(records, entity_ids, self.answer_embedding_collection, lambda record: record["answer"])
        self._insert_embeddings(records, entity_ids, self.full_embedding_collection, lambda record: 'Q:' + record["question"] + ';;; A: ' + record["answer"])

    def _insert_entities(self, records):
        owners = [record["owner"] for record in records]
        questions = [record["question"] for record in records]
        answers = [record["answer"] for record in records]
        entity_data = [owners, questions, answers]
        entity_ids = self.entities_collection.insert(entity_data, using='default')
        return entity_ids

    def _insert_embeddings(self, records, entity_ids, collection, text_func):
        embeddings = [create_embedding(text_func(record)) for record in records]
        embedding_data = [embeddings, entity_ids]
        collection.insert(embedding_data, using='default')

    def append_results(self, search_results, results):
        for hit in search_results[0]:
            print(f"hit: {hit.score}, entity_id: {hit.entity.get('entity_id')}")
            if (1 - hit.score) >= 0.77:  # Add this line to filter results by score
                entity = self.entities_collection.get(hit.entity.get('entity_id'), using='default')
                record = {
                    "id": hit.id,
                    "entity_id": hit.entity.get('entity_id'),
                    "owner": entity.entity.get('owner'),
                    "score": hit.score,
                    "question": entity.entity.get('question'),
                    "answer": entity.entity.get('answer')
                }
                if not any(res['question'] == record['question'] and res['owner'] == record['owner'] for res in results):
                    results.append(record)

    def search_records(self, query, top_k):
        # Generate embeddings for the query
        query_embeddings = create_embedding(query)

        # Consider saving the new embedding if couldn't find in db, give initial data: "I don't know, this requires an answer"
        # Search for similar records in Milvus
        print(f"searching for: {query}")
        search_results_by_questions = self._search_embedding_collection(self.question_embedding_collection, query_embeddings, top_k)
        search_results_by_answers = self._search_embedding_collection(self.answer_embedding_collection, query_embeddings, top_k)
        search_results_by_full = self._search_embedding_collection(self.full_embedding_collection, query_embeddings, top_k)
        print(f"found: {len(search_results_by_questions)} results")

        # Convert search results to a format that can be serialized to JSON
        results = []
       
