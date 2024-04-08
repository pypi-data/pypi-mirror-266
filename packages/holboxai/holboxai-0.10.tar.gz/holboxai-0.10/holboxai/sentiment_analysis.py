from jinja2 import Template
import json
import boto3
import openai




'''
prompt template for titam model.
'''

titan_template="""
I need one word sentiment of the sentence which
is between the <data> XML like tags.
The sentiment might be positive, negative or neutral.

<data>
{{ content }}
</data>
"""

'''
prompt template for cohere model.
'''
cohere_template = """
Analysis the sentiment of the sentence which
is between the <data> XML like tags.
give one word output. Choose from positive, negative or neutral.

<data>
{{ content }}
</data>


Consider the following examples:
sentence: The food is testy:
response: positive

sentence: The tea is not good.
response: negative
"""

claude_template="""
I need a one word sentiment of the sentence that i provide below.
Choose sentimnet from positive, negative or neutral.
{{ content }}
"""

class SentimentAnalysis:
    
    """
    A class for getting sentiment of a given text or sentence.
    
    This class will give functionality to use openai and bedrock
    to get sentimnet of the text.
    
    Methods:
        __init__(self):
        This initalized the bedrock runtime environment.
        
        get_openai_sentiment(self, text:str, llm_key):
            Args: 
                text:provided text or sentence
                llm_key: openai api key 
            returns: 
                Returns whether the text is negative or positive.
       
        get_sentiment(self, text:str, model:str=None):
            Args: 
                text:prvided text or sentence
                model:
                    The supported models are "amazon.titan-text-express-v1" and "anthropic.claude-3-sonnet-20240229-v1:0", and in default it uses cohere.command-text-v14.
                    If you don't provide any model, the default it use is cohere.
            returns: 
                Negative, positive or neutral sentiment.
    """
    
    def __init__(self):
        try:
            self.bedrock_runtime = boto3.client("bedrock-runtime")
        
        except Exception as e:
            print(e)
        
    def get_openai_sentiment(self, text:str, llm_key):
        '''
        Function for getting sentiment using openai
        get_openai_sentiment(self, text:str, llm_key):
            Args: 
                text:prvided text or sentence
                llm_key: openai api key 
            returns: 
                Returns whether the text is negative or positive.
        '''
        try:
            api_key = llm_key
            openai.api_key = api_key

            response = openai.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=f"Sentiment analysis of the given text:\n{text}\n",
                max_tokens=7,
                temperature=0
            )

            sentiment = response.choices[0].text.strip()
            return sentiment
        
        except Exception as e:
            print(e)
    
    def get_sentiment(self, text:str, model:str=None):
        '''
        Function for getting sentiment using amazon bedrock
        get_sentiment(self, text:str, model:str=None):
            Args: 
                text:prvided text or sentence
                model:
                    The supported models are "amazon.titan-text-express-v1" and "anthropic.claude-3-sonnet-20240229-v1:0", and in default it uses cohere.command-text-v14.
                    If you don't provide any model, the default it use is cohere.
            returns: 
                Negative, positive or neutral sentiment.
        '''
        try:
            if model == None:
                template = Template(cohere_template)
                prompt = template.render(content=text)
                
                kwargs = {
                    "modelId": "cohere.command-text-v14",
                    "contentType": "application/json",
                    "accept": "application/json",
                    "body":json.dumps(
                        {
                            "prompt": prompt,
                            "max_tokens": 15, 
                            "temperature": 0.5, 
                            "p":0.9
                        }
                    )
                }
                
                response = self.bedrock_runtime.invoke_model(**kwargs)
                response_body = json.loads(response.get('body').read())
                return response_body['generations'][0]['text']
            
            
            if model == "Amazon Titan":
                template = Template(titan_template)
                prompt = template.render(content=text)
                kwargs = {
                    "modelId": "amazon.titan-text-express-v1",
                    "contentType": "application/json",
                    "accept": "*/*",
                    "body": json.dumps(
                        {
                            "inputText": prompt,
                            "textGenerationConfig": {
                                "maxTokenCount": 512,
                                "temperature": 0,
                                "topP": 0.9
                            }
                        }
                    )
                }

                response = self.bedrock_runtime.invoke_model(**kwargs)
                response_body = json.loads(response.get('body').read())
                generation = response_body['results'][0]['outputText']
                return generation
            
            if model == "Anthropic Claude":
                template = Template(claude_template)
                prompt = template.render(content=text)
                kwargs = {
                    "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
                    "contentType": "application/json",
                    "accept": "application/json",
                    "body": json.dumps(
                        {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 200, 
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                        }
                    )    
                }
                response = self.bedrock_runtime.invoke_model(**kwargs)
                response_body = json.loads(response.get('body').read())
                return response_body['content'][0]['text']
        
        except Exception as e:
            print(e)


