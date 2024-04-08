from pandasai import SmartDataframe, SmartDatalake
from pandasai.llm import BedrockClaude
import boto3

class CsvQuery:
    """
    A class for querying CSV data using a language model.

    This class initializes a connection to the Bedrock runtime and provides methods
    for querying single or multiple CSV files using a language model for natural language
    processing.

    Methods:
        __init__(): Initializes the CsvQuery class by setting up the Bedrock runtime and language model.
        single_csv_query(df, query: str): Queries a single CSV file represented as a dataframe.
            Args:
                df (DataFrame): The dataframe to query.
                query (str): The natural language query to process.
            Returns:
                Any: The result of the query processed by the language model, or an exception if an error occurs.
        multi_csv_query(dfs: list, query: str): Queries multiple CSV files represented as a list of dataframes.
            Args:
                dfs (list of DataFrame): The dataframes to query.
                query (str): The natural language query to process.
            Returns:
                Any: The result of the query processed by the language model, or an exception if an error occurs.
    """
    def __init__(self):
        try:
            # Initialize a boto3 client for the Bedrock runtime
            self.bedrock_runtime = boto3.client("bedrock-runtime")
            # Initialize the language model with the Bedrock runtime client
            self.llm = BedrockClaude(self.bedrock_runtime)
        except Exception as e:
            # Print the exception if initialization fails
            print(e)
         
    def single_csv_query(self, df, query: str):
        """
        Queries a single CSV file represented as a dataframe.

        Args:
            df (DataFrame): The dataframe to query.
            query (str): The natural language query to process.

        Returns:
            Any: The result of the query processed by the language model, or an exception if an error occurs.
        """
        try:
            # Initialize a SmartDataframe with the dataframe and language model configuration
            dataframe = SmartDataframe(df, config={"llm": self.llm})
            # Process the query using the SmartDataframe and return the result
            result = dataframe.chat(query)
            return result
        except Exception as e:
            # Return the exception if an error occurs during query processing
            return e 

    def multi_csv_query(self, dfs: list, query: str):
        """
        Queries multiple CSV files represented as a list of dataframes.

        Args:
            dfs (list of DataFrame): The dataframes to query.
            query (str): The natural language query to process.

        Returns:
            Any: The result of the query processed by the language model, or an exception if an error occurs.
        """
        try:
            # Initialize a SmartDatalake with the list of dataframes and language model configuration
            lake = SmartDatalake(dfs, config={"llm": self.llm})
            # Process the query using the SmartDatalake and return the result
            result = lake.chat(query)
            return result
        except Exception as e:
            # Return the exception if an error occurs during query processing
            return e