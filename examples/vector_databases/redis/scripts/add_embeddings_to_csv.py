# Updated Code

import pandas as pd
import csv
import threading
from queue import Queue
import time

# Assume create_embedding function exists
# from scripts.create_embedding import create_embedding

# Create a semaphore with a maximum of 10 concurrent threads
semaphore = threading.Semaphore(10)

def worker(q, results):
    with semaphore:
        while not q.empty():
            item = q.get()
            vector = create_embedding(item)
            results.append(vector)
            q.task_done()

def process_item_with_threading(queue, results):
    thread = threading.Thread(target=worker, args=(queue, results))
    thread.start()
    return thread  # Return the thread so we can join it later

def add_embeddings_to_csv(file_path: str):
    df = pd.read_csv(file_path)

    gpt_vectors = []

    vector_ids = []

    threads = []  # Keep track of all threads

    id_counter = 1
    for _, row in df.iterrows():
        question = row['answer'] + ' ' + row['question']

        gpt_queue = Queue()

        gpt_queue.put(question)

        gpt_results = []

        # Start the threads and keep track of them
        threads.append(process_item_with_threading(gpt_queue, gpt_results))

        gpt_vectors.append(gpt_results[0])
        vector_ids.append(id_counter)

        id_counter += 1

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    df['gpt_vector'] = gpt_vectors
    df['vector_id'] = vector_ids

    df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)

# Specify the path to your CSV file
# csv_file_path = 'path_to_your_csv_file.csv'
# add_embeddings_to_csv(csv_file_path)

