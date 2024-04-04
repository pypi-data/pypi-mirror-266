import pkg_resources
import csv
import pandas as pd

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
        pass
    
    def queries(self, qid):
        return
    def query_text(self, qid):
        return

    def query_data(self, qid):
        data_file_path = pkg_resources.resource_filename('autopipeline', f'data/{qid}/data.csv')
        df = pd.read_csv(data_file_path)
        return df
    def query_answer(self, qid):
        data_file_path = pkg_resources.resource_filename('autopipeline', f'data/{qid}/answer.csv')
        df = pd.read_csv(data_file_path)
        return df

    def query(self, qid):
        # Function to load query, data, and answer altogether
        query = self.load_query(qid)
        data = self.load_data(qid)
        answer = self.load_answer(qid)
        return {
            "query": query,
            "data": data,
            "answer": answer
        }


