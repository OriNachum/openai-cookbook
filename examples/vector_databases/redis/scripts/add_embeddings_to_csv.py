# Updated Code

import pandas as pd
import csv
import threading
from queue import Queue
import time

# Assume create_embedding function exists
from scripts.create_embedding import create_embedding

# Create a semaphore with a maximum of 10 concurrent threads
semaphore = threading.Semaphore(10)

def worker(q, results, vectors, ids, id_counter):
    with semaphore:
        while not q.empty():
            item = q.get()
            vector = create_embedding(item)
            results.append(vector)
            vectors.append(vector)
            ids.append(id_counter)
            id_counter += 1
            q.task_done()

def process_item_with_threading(queue, results, vectors, ids, id_counter):
    thread = threading.Thread(target=worker, args=(queue, results, vectors, ids, id_counter))
    thread.start()
    return thread  # Return the thread so we can join it later

import concurrent.futures

def add_embeddings_to_csv(file_path: str):
    df = pd.read_csv(file_path)

    question_vectors = []
    answer_vectors = []

    vector_ids = []

    id_counter = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for _, row in df.iterrows():
            question = row['question']
            answer = row['answer']

            question_future = executor.submit(create_embedding, question)
            answer_future = executor.submit(create_embedding, answer)

            # Wait for the futures to complete and get their results
            question_result = question_future.result()
            answer_result = answer_future.result()

            question_vectors.append(question_result)
            answer_vectors.append(answer_result)
            vector_ids.append(id_counter)

            id_counter += 1

    df['question_vector'] = question_vectors
    df['answer_vector'] = answer_vectors
    df['vector_id'] = vector_ids

    df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)

# Specify the path to your CSV file
# csv_file_path = 'path_to_your_csv_file.csv'
# add_embeddings_to_csv(csv_file_path)

