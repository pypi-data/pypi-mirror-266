from .data import load_query, load_data, load_answer
from .Interactive import pipeline

def evaluate(qid):
    query = load_query(qid)
    table, desc = load_data(qid)
    result, augmented_table = pipeline(query, table, desc)
    answer = load_answer(qid)

    # Comparison logic
    
    return 