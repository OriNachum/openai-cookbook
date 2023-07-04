import csv
from typing import List
from datetime import date

class NewRecord:
    def __init__(self, question: str, answer: str, date: date, company_name: str, company_size: str, company_location: str, company_industry: str):
        self.question = question
        self.answer = answer
        self.date = date
        self.company_name = company_name
        self.company_size = company_size
        self.company_location = company_location
        self.company_industry = company_industry

def convert_newrecordlist_to_csv(records: List[NewRecord], filename: str):
    with open(filename, mode='x', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["question", "answer", "date", "company_name", "company_size", "company_location", "company_industry"])  # Write the header

        for record in records:
            writer.writerow([record.question, record.answer, record.date, record.company_name, record.company_size, record.company_location, record.company_industry])
