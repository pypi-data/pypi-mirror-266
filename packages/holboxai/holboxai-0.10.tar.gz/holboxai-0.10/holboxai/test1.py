from s3_reader import S3DocReader
from csv_query import CsvQuery
from docs_query import DocsQuery
import pandas as pd
from sentiment_analysis import SentimentAnalysis
from name_entity_recognition import NameEntityRecognition
from text2image import text2image
from summarizer import Summarizer
from relevant_docs import RelevantDocs

# ## S3 files Reader 

# reader = S3DocReader()
# docs = reader.get_docs("gen-ai-for-automotive")
# print(docs)
# print("s3docreader done")

# ## RAG in S3 Documents : 

# docsQuery = DocsQuery()
# indexes = docsQuery.create_index(docs)
# query = "what are the sales of maruti"  # Your query here
# response = docsQuery.query(indexes, query)
# print(response)
# print("rag done")

# ## Semantic Search 

# query = "which 3 companies leads the sales growth in january"
# rel_docs = RelevantDocs()
# docs = rel_docs.get_docs(query=query, n_docs=4, retriever=indexes)
# print(docs)
# print("semantic done")

## RAG in csv file

# ib = CsvQuery()
# query = "what is the total value"
# df = pd.read_csv("/home/ubuntu/RAG_API/csv_file/Air_Quality.csv")
# response = ib.single_csv_query(df, query)
# print(response) 
# print({"csv done"})

## Image generation 

# txt2img = text2image()
# prompt = "a baby riding formula 1 car" 
# txt2img.generate_image(prompt, 5, 25) # example : cfg_scale = 5 , inference_steps = 25 


## Document Summarization 

# reader = S3DocReader()
# docs = reader.get_file(bucket_name="gen-ai-for-lifescience",file_name = "CRISPR revolutionized.txt")
# doc_summary = Summarizer()
# summary = doc_summary.summarize(docs)
# print(summary)
# print("summarizer done")

## Sentiment Analysis on text

# # Sentiment using cohere.command-text-v14

# sa = SentimentAnalysis()
# response1 = sa.get_sentiment("I'm extremely disappointed with the quality of the product. It broke after just one week of use.")
# print(response1)


# # Sentiment using anthropic.claude-3-sonnet-20240229-v1:0

# response2 = sa.get_sentiment("I'm extremely disappointed with the quality of the product. It broke after just one week of use.", "anthropic.claude-3-sonnet-20240229-v1:0")
# print(response2)


# # Sentiment using amazon.titan-text-express-v1

# response3 = sa.get_sentiment("I'm extremely happy with the quality of the product. It was amazing after just one week of use.", "amazon.titan-text-express-v1")
# print(response3)




## Name Entity Recognition

# # Using cohere.command-text-v14

# ner = NameEntityRecognition()
# response = ner.get_entity("Harry and jay are going for a party in dubai, after that they will visit paris.")
# print(response)

# # # Using anthropic.claude-3-sonnet-20240229-v1:0

# response = ner.get_entity("Harry and jay are going for a party in dubai, after that they will visit paris.", "anthropic.claude-3-sonnet-20240229-v1:0")
# print(response)

# # # Using amazon.titan-text-express-v1

# response = ner.get_entity("Harry and jay are going for a party in dubai, after that they will visit paris.", "amazon.titan-text-express-v1")
# print(response)

