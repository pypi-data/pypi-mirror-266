import openai
import os
from .util import num_tokens_from_string, num_tokens_from_messages, num_tokens_from_functions

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# print(openai.api_key)


def query_sql(user_query, enum, desc, status, client):
    # Define the user's query as an argument
    messages = [
        {
            "role": "system",
            "content": 
            '''
            Table table, columns = ''' + str(enum) + ''' where ''' + desc +
            '''Your task is to generate a SQL query that can be executed on this database based on users' queries. 
            The query should be supported in SQLite.
            ATTENTION: the values are case-sensitive, and you should strictly follow their provided formats and sample values (if any).
            '''

        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases."
        },
        {
            "role": "assistant",
            "content": "SELECT COUNT(*) FROM table WHERE case_summary_sentiment = 'Positive'"
        },
        {
            "role": "user",
            "content": "I want to count the number of cases with person(s) mentioned in their case descriptions."
        },
        {
            "role": "assistant",
            "content": "SELECT COUNT(*) FROM table WHERE case_ner LIKE '%PER%'"
        },
        {
            "role": "user",
            "content": user_query  # Use the user's query
        }
    ]

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-0613",
        messages=messages
    )

    status.append('code generated')

    return response.choices[0].message['content'], status

def query_pd(user_query, enum, desc, status, verbose, client):
    # Define the user's query as an argument
    messages = [
        {
            "role": "system",
            "content": 
            '''
            pandas dataframe table, columns = ''' + str(enum) + ''' . ''' +
            '''Your task is to generate pandas code that 
            1. can be executed directly on this pandas dataframe based on users' queries;
            2. the code should produce correct results based on the SAMPLE VALUES AND DESCRPITIONS of each column.''' + desc + '''
            ATTENTION: the values are case-sensitive, and you should strictly follow their provided formats and sample values (if any).
            The code can be of multiple lines, BUT the final assignment has to be assigned to res;
            Example: res = table['case'].count();
            IMPORTANT: Return the code snippets ONLY. You are not allowed to output anything else.
            ATTENTION: When you think there are more than one ways to write code to answer user query OR unsure about how to generate the code OR need some further details OR assumptions, return the entire table as res.
            '''

        },
        # {
        #     "role": "user",
        #     "content": "I want to count the number of positive summaries on the cases."
        # },
        # {
        #     "role": "assistant",
        #     "content": "res = table[table['case_summary_sentiment'] == 'Positive'].shape[0]"
        # },
        # {
        #     "role": "user",
        #     "content": "I want to count the number of cases with person(s) mentioned in their case descriptions."
        # },
        # {
        #     "role": "assistant",
        #     "content": "res = table[table['case_ner'].str.contains('PER')].shape[0]"
        # },
        {
            "role": "user",
            "content": "I want to generate stories based on summaries."
        },
        {
            "role": "assistant",
            "content": "res = table"
        },
        # {
        #     "role": "user",
        #     "content": "I want to check if the 'x' column of row 0 contains misinformation."
        # },
        # {
        #     "role": "assistant",
        #     "content": "res = (legal_case[0]['x_misinfo'] == 'misinfo')"
        # },
        # {
        #     "role": "user",
        #     "content": "I want to check if the 'x' column of row 0 is real."
        # },
        # {
        #     "role": "assistant",
        #     "content": "res = (legal_case[0]['x_misinfo'] == 'real')"
        # },
        # {
        #     "role": "user",
        #     "content": "I want to check if the 'x' column of row 0 doesn't contain any hate speech."
        # },
        {
            "role": "user",
            "content": "I am given a table with the following columns and format/values: "+desc+" "+user_query  # Use the user's query
        }
    ]

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-0613",
        messages=messages
    )
    if verbose:
        num_token_msg = num_tokens_from_messages(messages, "gpt-4-0613")
        print("Number of tokens of messages for 'query_pd': ", num_token_msg)
        print("******Number of prompt tokens for 'query_pd': ", response.usage.prompt_tokens)
        print("******Number of answer tokens for 'query_pd': ", response.usage.completion_tokens)
        print("******Number of total tokens for 'query_pd': ", response.usage.total_tokens)

    status.append('code generated')

    return response.choices[0].message.content, status