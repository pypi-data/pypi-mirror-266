from langchain_community.llms import Bedrock
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.llm import LLMChain
from langchain import hub
from langchain.chains.combine_documents.stuff import StuffDocumentsChain



class Summarizer:
    
    def __init__(self): 
        try : 
            self.llm = Bedrock(model_id="mistral.mistral-large-2402-v1:0")
            self.map_prompt = hub.pull("rlm/map-prompt")
            self.reduce_prompt = hub.pull("rlm/map-prompt")
        
        except Exception as e: 
            print("You might not have the access of LLM with modelid :mistral.mistral-large-2402-v1:0")
    
    def summarize(self,docs):
        try:
            map_chain = LLMChain(llm=self.llm, prompt=self.map_prompt)
            reduce_chain = LLMChain(llm=self.llm, prompt=self.reduce_prompt)

            # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
            combine_documents_chain = StuffDocumentsChain(
                llm_chain=reduce_chain, document_variable_name="docs"
            )

            # Combines and iteratively reduces the mapped documents
            reduce_documents_chain = ReduceDocumentsChain(
                # This is final chain that is called.
                combine_documents_chain=combine_documents_chain,
                # If documents exceed context for `StuffDocumentsChain`
                collapse_documents_chain=combine_documents_chain,
                # The maximum number of tokens to group documents into.
                token_max=4000,
            )
            map_reduce_chain = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="docs",
            # Return the results of the map steps in the output
            return_intermediate_steps=False,
            )
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
            split_docs = text_splitter.split_documents(docs)
            result = map_reduce_chain.run(split_docs)
            return result
        
        except Exception as e :
            return e 
        