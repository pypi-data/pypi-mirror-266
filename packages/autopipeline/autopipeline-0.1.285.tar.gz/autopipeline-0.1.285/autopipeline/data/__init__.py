import pkg_resources
import csv
import pandas as pd
import importlib.resources as resources
from pathlib import Path

def get_persuasion_effect_data():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/persuasive-17.csv')
    df = pd.read_csv(data_file_path)
    df = df[['sentence']]
    return df

def get_toxic_data():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/toxic.csv')
    df = pd.read_csv(data_file_path)
    df = df[['original_sentence']]
    return df

def get_dog_whistle_data():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/dogwhistle.tsv')
    df = pd.read_csv(data_file_path, on_bad_lines='skip', delimiter='\t')
    df = df[['Linguistic Context']]
    return df

def get_ner_data():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/ner.csv')
    df = pd.read_csv(data_file_path)
    return df

def get_pos_data():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/ner.csv')
    df = pd.read_csv(data_file_path)
    return df

def get_case_data():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/ner.csv')
    df = pd.read_csv(data_file_path)
    return df

def get_pdf_doc():
    data_file_path = pkg_resources.resource_filename('autopipeline', 'data/legal-doc.csv')
    df = pd.read_csv(data_file_path)
    return df

class QUIET_ML:
    def __init__(self):
        # Initialize if needed
        data_file_path = pkg_resources.resource_filename('autopipeline', f'data/queries.csv')
        df = pd.read_csv(data_file_path)
        self.queries = df
        data_file_path = pkg_resources.resource_filename('autopipeline', f'data/desc.csv')
        df = pd.read_csv(data_file_path)
        self.desc = df
    
    # def queries(self, qid):
    #     return
    def query_text(self, qid):
        return self.queries[self.queries["QID"]==qid]["Query"]
    
    def query_desc(self, qid):
        return self.desc[self.desc["QID"]==qid]["Description"]
    
    def query_data(self, qid):
        data_file_path = pkg_resources.resource_filename('autopipeline', f'data/{qid}/data.csv')
        df = pd.read_csv(data_file_path)
        return df
    
    def query_answer(self, qid):
        # data_file_path = pkg_resources.resource_filename('autopipeline', f'data/{qid}/answer.csv')
        # df = pd.read_csv(data_file_path)
        if qid == 8:
            return [0.9401709401709402]
        elif qid == 29:
            dataframes = [38.51447912749153]
        elif qid == 30:
            dataframes = [39.32038834951456]
        elif qid == 31:
            dataframes = [['Jessica Rabbit', 'Tina Carlyle', 'Susie Diamond', 'Sugar Kane Kowalczyk', 'Dorothy Vallens', 'Ellen Aim']]
        else:
            dataframes = []
        package_name = 'autopipeline'
        directory_name = f'data/{qid}'

        # dataframes = []  # List to store each DataFrame

        # Access the directory as a Path object
        with resources.files(package_name) as pkg_path:
            directory_path = pkg_path / directory_name

            # List all CSV files that start with 'answer'
            all_files = [f for f in directory_path.iterdir() if f.is_file() and f.name.startswith('answer') and f.name.endswith('.csv')]

            # Read each CSV file into a DataFrame and append it to the list
            for file_path in all_files:
                df = pd.read_csv(file_path)
                dataframes.append(df)

        return dataframes

    def query(self, qid):
        # Function to load query, data, desc, and answer altogether
        query = self.query_text(qid)
        data = self.query_data(qid)
        answer = self.query_answer(qid)[0]
        description = self.query_desc(qid)
        return {
            "query": query,
            "data": data,
            "desc": description,
            "answer": answer
        }


