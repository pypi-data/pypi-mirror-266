from langchain_community.vectorstores import FAISS

class RelevantDocs:
    """
    A class to retrieve relevant documents based on a query using a retriever object.

    This class is designed to interact with a retriever, which is typically an instance
    of a vector store such as FAISS, to find and return documents that are relevant to
    a given query.

    Methods:
        get_docs(query, n_docs, retriever): Retrieves a specified number of documents relevant to the query.
            Args:
                query (str): The query string to search for relevant documents.
                n_docs (int): The number of relevant documents to retrieve.
                retriever (object): The retriever instance to use for finding relevant documents.
            Returns:
                list of str: A list of documents that are relevant to the query.
    """
    def get_docs(self, query, n_docs, retriever):
        try:
            # Configure the retriever to search for a specified number of documents
            retriever = retriever.as_retriever(search_kwargs={"k": n_docs})
            # Retrieve documents relevant to the query
            docs = retriever.get_relevant_documents(query)
            docs_list = []
            # Iterate over the retrieved documents and add their content to the list
            for i in range(len(docs)):
                doc = ""
                # Extract the page content from each document
                response = docs[i].page_content
                doc += response
                docs_list.append(doc)
            return docs_list
        
        except Exception as e:
            # Return the exception if an error occurs
            return e