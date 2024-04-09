import pandas as pd
import os
import autopipeline
from openai import OpenAI
from .PipelineGen import pipeline_gen
from .Mapping import base_table_gen
from .Filter import check_vague
from .util import register_func


def load_data(dataframe, desc, desc_file=True):
    # Load DataFrame
    try:
        table = pd.read_csv(dataframe)  # or pd.read_excel for Excel files
    except Exception as e:
        print(f"Failed to load DataFrame: {e}")
        return
    if desc_file:
        try:
            with open(desc, 'r') as file:
                description = file.read()
        except:
            print(f"Failed to load description: {e}")
            return
    else:
        description = desc
    
    return table, description

def pipeline(query, table_ptr, description, verbose = False, udf = None):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    client = OpenAI(api_key=autopipeline.api_key, organization=autopipeline.organization)

    table = table_ptr.copy()
    columns = str(table.columns.tolist())

    print("********** Checking Query...")
    if udf == None:
        precheck, functions = check_vague(query, columns, description, verbose, client)
    else:
        func_desc = ""
        for f in udf:
            f['func-name'] = f["func"].__name__
        for f in udf:
            func_desc += (f['func-name'] + " : " + f['func-description'] + "\n")
            register_func(f["func-name"], f["func"])
        precheck, functions = check_vague(query, columns, description, verbose, client, func_desc)
    # precheck = precheck["content"]
    precheck = precheck.content
    if verbose:
        print("########## Precheck Result:", precheck)
        print("\n")
    ls = precheck.split('#')
    res = ls[0]
    hint = ls[1]
    if res == "False":
        print("########## Feedback: ", hint)
        print("\n")
        if verbose: # print functions only when verbose
            print("\nThe supported function list is as follows: \n" + functions)
        print("Please Be More Detailed on Query.")
        print("\n")
        return None, table
    if "WARNING" in hint:
        warning_msg = "WARNING: "+hint.split("WARNING:")[1].strip()
        print("########## "+warning_msg)
        user_reponse = str(input("Proceed? [Y/n]"))
        if user_reponse == "Y":
            hint = hint.split("WARNING")[0].strip()
        else:
            return None, table
    print("********** Query Check Pass!")

    require_new, feedback, result, table = pipeline_gen(query, table, description, hint, verbose, client, udf, table_type="pd")
    if require_new:
        print("########## Feedback: ", feedback)
        print("\n")
        print("Please Be More Detailed on Query.")
        print("\n")
    else:
        print("Succeed!")
        print("\n")
    return result, table

def interactive_pipeline(table, description):
    require_new = True
    # table, enum, description = base_table_gen()
    while require_new:
        print("-----------------------------")
        query = str(input("Please enter your query: "))
        print("\n")
        columns = str(table.columns.tolist())
        precheck, functions = check_vague(query, columns, description)
        precheck = precheck["content"]
        print("########## Precheck Result:", precheck)
        print("\n")
        ls = precheck.split('#')
        res = ls[0]
        hint = ls[1]
        if res == "False":
            print("########## Feedback: ", hint)
            print("\n")
            print("\nThe supported function list is as follows: \n" + functions)
            require_new = True
            continue
        require_new, feedback = pipeline_gen(query, table, description, table_type="pd")
        if require_new:
            print("########## Feedback: ", feedback)
            print("\n")


def _interactive_pipeline():
    # Prompt user for file path
    file_path = input("Please enter the file path for your DataFrame: ")

    # Load DataFrame
    try:
        table = pd.read_csv(file_path)  # or pd.read_excel for Excel files
    except Exception as e:
        print(f"Failed to load DataFrame: {e}")
        return
    
    # Prompt user for file path
    file_path = input("Please enter the description for your DataFrame: ")

    # Load DataFrame
    try:
        with open(file_path, 'r') as file:
            description = file.read()
    except:
        description = file_path
    require_new = True
    # table, enum, description = base_table_gen()
    while require_new:
        print("-----------------------------")
        query = str(input("Please enter your query: "))
        require_new, feedback = pipeline_gen(query, table, description, table_type="pd")
        if require_new:
            print("########## Feedback: ", feedback)
            print("\n")

if __name__ == "__main__":
    interactive_pipeline()