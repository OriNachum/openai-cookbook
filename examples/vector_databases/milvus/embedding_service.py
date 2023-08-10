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
                FieldSchema(name='owner', dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name='question', dtype=DataType.VARCHAR, max_length=64000),
                FieldSchema(name='answer', dtype=DataType.VARCHAR, max_length=64000),
                FieldSchema(name='question_embedding', dtype=DataType.FLOAT_VECTOR, dim=1536),
                #FieldSchema(name='answer_embedding', dtype=DataType.FLOAT_VECTOR, dim=1536),
                #FieldSchema(name='full_embedding', dtype=DataType.FLOAT_VECTOR, dim=1536)
            ]
            schema = CollectionSchema(fields=fields, description="Book Collection", auto_id=True)
            self.collection = Collection(name=self.collection_name, schema=schema, using='default')

            # Create the index on the collection and load it.
            index_param = {
                'metric_type': 'L2',
                'index_type': 'HNSW',
                'params': {'M': 8, 'efConstruction': 64}
            }
            self.collection.create_index("question_embedding", index_param)
            #self.collection.create_index("answer_embedding", index_param)
            #self.collection.create_index("full_embedding", index_param)

            self.collection.load()
        else:
            # If the collection already exists, just load it
            self.collection = Collection(name=self.collection_name)
            self.collection.load()

    def pre_phrase(self, text):
        # Define a system prompt for pre-phrasing
        prompt = "As a data scientist specializing in text rephrasing for embedding generation, you are tasked with processing snippets from conversations or FAQs. Your goal is to rephrase these sentences to highlight the most critical information. Aim for a rephrase that maintains essential details while minimizing irrelevant noise. Remember, the ultimate goal is to optimize these phrases for embedding generation within a vector database."

        # Pre-phrase the text
        text = complete_prompt(text, prompt, "gpt-3.5-turbo", 0.05)
        
        return text

    def insert_records(self, records):
        # Generate embeddings for all records
        question_embeddings = [create_embedding(record["question"]) for record in records]
        #answer_embeddings = [self.generate_embeddings(record["answer"]) for record in records]
        #full_embeddings = [self.generate_embeddings('Q:' + record["question"] + ';;; A: ' + record["answer"]) for record in records]
        owners = [record["owner"] for record in records]
        questions = [record["question"] for record in records]
        answers = [record["answer"] for record in records]
        
        print(f"Dimensions of embedding for record {question_embeddings[0]}: {len(question_embeddings[0])}")
        print(f"Data type of first element in embedding: {type(question_embeddings[0][0])}")

        print(f"Questions: {questions}, Type: {type(questions[0])}")
        print(f"Answers: {answers}, Type: {type(answers[0])}")
        print(f"Embeddings: {len(question_embeddings)}, Embedding Length: {len(question_embeddings[0])}, Type: {type(question_embeddings[0][0])}")
        
        data = []
        data.append(owners)
        data.append(questions)
        data.append(answers)
        data.append(question_embeddings)
        #data.append(answer_embeddings)
        #data.append(full_embeddings)

        # Insert records into Milvus
        #self.collection.insert({"title": titles, "description": descriptions, "embedding": embeddings}, using='default')
        self.collection.insert(data, using='default')

    def append_results(self, search_results_by_questions, results):
        for hit in search_results_by_questions[0]:
            print(f"hit: {hit.score}, owner: {hit.entity.get('owner')}, question: {hit.entity.get('question')}, answer: {hit.entity.get('answer')}")
            if hit.score >= 0.77:  # Add this line to filter results by score
                record = {
                    "id": hit.id,
                    "owner": hit.entity.get('owner'),
                    "score": hit.score,
                    "question": hit.entity.get('question'),
                    "answer": hit.entity.get('answer')
                }
                if not any(res['question'] == record['question'] and res['owner'] == record['owner'] for res in results):
                    results.append(record)

    def search_records(self, query, top_k):
        # Generate embeddings for the query
        query_embeddings = create_embedding(query)
        
        # Consider saving the new embedding if couldn't find in db, give initial data: "I don't know, this requires an answer"
        # Search for similar records in Milvus
        search_results_by_questions = self.collection.search([query_embeddings], "question_embedding", param={"metric_type": "L2"},limit=top_k, output_fields=['question', 'answer'], using='default')
        #search_results_by_answers = self.collection.search([query_embeddings], "answer_embedding", param={"metric_type": "L2"},limit=top_k, output_fields=['question', 'answer'], using='default')
        #search_results_by_full = self.collection.search([query_embeddings], "full_embedding", param={"metric_type": "L2"},limit=top_k, output_fields=['question', 'answer'], using='default')

        # Convert search results to a format that can be serialized to JSON
        results = []
        self.append_results(search_results_by_questions, results)
        #self.append_results(search_results_by_answers, results)
        #self.append_results(search_results_by_full, results)

        if not results:
            return ["I don't know"]
        
        results.sort(key=lambda x: x['score'], reverse=True)
        best_results = results[:top_k]

        # If there are results, use them to generate a prompt for GPT-3.5-turbo
        system_prompt = "As an AI, your task is to answer the query using only the provided information. Stick to the facts, avoid making assumptions or adding personal interpretations, and do not use any previously stored data."
        data = "\\n".join([f'Q: {result["question"]}: {result["answer"]}' for result in best_results])
        data = f'Please answer the following question based only the Answers that following it. Do not answer based on any other source. Q: {query}\\n Answers:\\n{data}'
        answer = complete_prompt(data, system_prompt, "gpt-3.5-turbo", 0.05)
        return [answer]

