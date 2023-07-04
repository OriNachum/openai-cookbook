import csv
import os
from typing import List
from datetime import date

from scripts.generate_unique_public_id import generate_unique_public_id

class NewRecord:
    def __init__(self, question: str, company_name: str, company_size: str, company_location: str, company_industry: str):
        self.question = question
        #self.answer = answer
        #self.date = date
        self.companyName = company_name
        self.companySize = company_size
        self.companyCountry = company_location
        self.companyIndustry = company_industry

def convert_newrecordlist_to_csv(records: List[NewRecord], filename: str):
    file_exists = os.path.isfile(filename)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id","question", "company_name", "company_size", "company_country", "company_industry"])  # Write the header
        for record in records:
            id=generate_unique_public_id()
            writer.writerow([id, record.question, record.companyName, record.companySize, record.companyCountry, record.companyIndustry])