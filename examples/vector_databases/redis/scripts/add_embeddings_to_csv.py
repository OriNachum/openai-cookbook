import pandas as pd
import csv

from scripts.create_embedding import create_embedding

def add_embeddings_to_csv(file_path: str):
    df = pd.read_csv(file_path)

    question_vectors = []
    vector_ids = []

    id_counter=1
    for _, row in df.iterrows():
        question = row['question']

        question_vector = create_embedding(question)

        question_vectors.append(question_vector)
        vector_ids.append(id_counter)

        id_counter += 1

    df['question_vector'] = question_vectors
    df['vector_id'] = vector_ids

    df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)

# Specify the path to your CSV file
# csv_file_path = 'path_to_your_csv_file.csv'
# add_embeddings_to_csv(csv_file_path)
