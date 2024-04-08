import boto3
from langchain_community.document_loaders import S3DirectoryLoader
from langchain_community.document_loaders import S3FileLoader
class S3DocReader:
    """
    A class for reading documents from an S3 bucket using the S3DirectoryLoader.

    This class initializes a boto3 session to interact with AWS S3 services and provides
    a method to retrieve documents from a specified S3 bucket.

    Methods:
        __init__(): Initializes the S3DocReader class by creating a boto3 session.
        get_bucket(bucket_name: str): Retrieves documents from the specified S3 bucket.
            Args:
                bucket_name (str): The name of the S3 bucket from which to retrieve documents.
            Returns:
                list: A list of documents retrieved from the S3 bucket, or an exception if an error occurs.
    """
    def __init__(self):
        try:
            # Initialize a boto3 session to interact with AWS services
            session = boto3.Session()
        except Exception as e:
            # Print the exception if the session initialization fails
            print(e)
    
    def get_docs(self, bucket_name: str):
        """
        Retrieves documents from the specified S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket from which to retrieve documents.

        Returns:
            list: A list of documents retrieved from the S3 bucket, or an exception if an error occurs.
        """
        try:
            # Initialize the S3DirectoryLoader with the specified bucket name
            loader = S3DirectoryLoader(bucket=bucket_name)
            # Load and return the documents from the S3 bucket
            docs = loader.load()
            return docs
        except Exception as e:
            # Return the exception if an error occurs during document retrieval
            print(e)
            return e
        
    
    def get_file(self,bucket_name,file_name):
        try:
            loader = S3FileLoader(bucket_name ,file_name)
            doc_file = loader.load()
            return doc_file
    
        except Exception as e :
            return e 

        

        
        

        
