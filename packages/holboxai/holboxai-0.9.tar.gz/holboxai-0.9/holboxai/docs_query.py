from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Bedrock
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain import hub   

class DocsQuery:
    """
    A class for creating and querying a document index using LangChain.

    This class utilizes various components from the LangChain library to split documents,
    generate embeddings, create an index, and perform queries against that index. It leverages
    the LangChain community's embeddings, vector stores, and large language models (LLMs) for
    document retrieval and question answering.

    Attributes:
        text_splitter (RecursiveCharacterTextSplitter): A text splitter for chunking documents.
        embeddings (BedrockEmbeddings): Embeddings model for generating document embeddings.
        llm (Bedrock): A large language model for generating responses based on retrieved documents.

    Methods:
        create_index(docs): Creates an index from a list of documents.
            Args:
                docs (list of str): The documents to index.
            Returns:
                FAISS: An FAISS index object for the documents.

        query(index, query): Queries the index with a specific question and returns an answer.
            Args:
                index (FAISS): The FAISS index object to query.
                query (str): The query or question to ask.
            Returns:
                str: The answer to the query, based on the indexed documents.
    """
    def __init__(self):
        # Initialize the text splitter with a specific chunk size and overlap.
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        # Initialize the embeddings model from Bedrock
        self.embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
        # Initialize the language model from Brdrock
        self.llm = Bedrock(model_id="mistral.mixtral-8x7b-instruct-v0:1")
        
    def create_index(self, docs):
        """
        Creates a FAISS index from the provided documents.
        
        Args:
            docs (list of str): A list of documents to index.
        
        Returns:
            FAISS: A FAISS index object or an exception if an error occurs.
        """
        try:
            # Split the documents into chunks for processing.
            documents = self.text_splitter.split_documents(docs)
            # Create a FAISS index from the document chunks and embeddings.
            retriever = FAISS.from_documents(documents, self.embeddings)
            return retriever
        except Exception as e:
            # Return the exception if something goes wrong.
            return e 
    
    def query(self, index, query):
        """
        Queries the index with the provided query string and returns the answer.
        
        Args:
            index (FAISS): The FAISS index object.
            query (str): The query string to search for in the index.
        
        Returns:
            str: The answer retrieved from the index or an exception if an error occurs.
        """
        try:
            # Pull the retrieval-qa-chat prompt from the hub.
            retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
            # Convert the index into a retriever object.
            retriever = index.as_retriever()
            # Create a chain that combines documents based on the query.
            combine_docs_chain = create_stuff_documents_chain(
                self.llm, retrieval_qa_chat_prompt
            )
            # Create a retrieval chain that uses the retriever and the combine_docs_chain.
            retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
            # Invoke the retrieval chain with the query and get the response.
            response = retrieval_chain.invoke({"input": query})
            # Return the answer from the response.
            return response['answer']
        except Exception as e:
            # Return the exception if something goes wrong.
            return e 