import boto3
import json
import jinja2
from jinja2 import Template

titan_template="""
You are a helpful assistant, analyse the sentence which
is between the <data> XML like tags.

identify and extract the name of a person and a place mentioned within the text.

Instructions:
1. Read the provided sentence carefully.
2. Look for mentions of names and places within the text.
3. Identify the name of a person mentioned in the sentence.
4. Identify the name of a place mentioned in the sentence.
5. Provide the extracted names of the person and the place.

Example Sentence:
"John went to Paris for a vacation."

Expected Output:
Person: John
Place: Paris

Please extract and provide the name of a person and a place mentioned in the sentence.
There might be multiple person and place.

<data>
{{ content }}
</data>

"""

cohere_template = '''
Given the following sentence,which
is between the <data> XML like tags.
extract the name of a person and a place mentioned within the content.

Instructions:
1. Read the provided sentence carefully.
2. Identify any mentions of names or places.
3. Extract the name of a person and a place from the content.
4. Provide the extracted names.
5. There might be multiple person and place. Provide all of them.
Example Sentence:
"The Smith family moved to San Francisco last year."

Expected Output:
Person: Smith family
Place: San Francisco

Example Sentence:
"John and Alice went to Paris and london for a vacation."

Expected Output:
Person: John, Alice
Place: Paris, london

Please extract and provide the name of a person and a place mentioned in the content.

<data>
{{ content }}
</data>
'''

claude_template = '''
Given the following text, which is enclosed within <data> XML-like tags, extract the name of a person and a place mentioned within the content.

Instructions:
1. Carefully examine the provided text within the <data> tags.
2. Extract the name of a person and a place from the content.
3. Provide the extracted names.
4. If there are multiple persons or places mentioned, provide all of them.
5. Take note of any variations or synonyms for names and places.
6. make two list one for person name and other for place name

Example Text:
"The Smith family moved to San Francisco last year."

Expected Output:
Person: Smith family
Place: San Francisco

Example Text:
"John and Alice went to Paris and London for a vacation."

Expected Output:
Person: John, Alice
Place: Paris, London

Please extract and provide the name of a person and a place mentioned in the content.

<data>
{{ content }}
</data>
'''
class NameEntityRecognition:
    
    '''
    A class for extracting names and entity from the text.
    
    This class will give functionality to use bedrock's different models
    to extract name and entity from text.
    
    Methods:
        __init__(self):
        This initalized the bedrock runtime environment.
        
        get_entity(self, text:str, model:str=None)
            args:
                text: provided text or sentence
                
                model:
                If model is none then the default model "cohere.command-text-v14" is use.
                
                Other options of models are:
                "amazon.titan-text-express-v1",
                "anthropic.claude-3-sonnet-20240229-v1:0"
            
            returns:
                A list of name and entity.
    '''
    
    def __init__(self):
        try:
            self.bedrock_runtime = boto3.client("bedrock-runtime")
        
        except Exception as e:
            print(e)
            
    def get_entity(self, text:str, model:str=None):
        '''
        Function to get list of names and entity.
        get_entity(self, text:str, model:str=None)
            args:
                text: provided text or sentence
                
                model:
                If model is none then the default model "cohere.command-text-v14" is use.
                
                Other options of models are:
                "amazon.titan-text-express-v1",
                "anthropic.claude-3-sonnet-20240229-v1:0"
            
            returns:
                A list of name and entity.
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
                            "max_tokens": 200, 
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
                
                
                
