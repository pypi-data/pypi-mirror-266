import base64
import json
import logging
import boto3
import io
from PIL import Image
from botocore.exceptions import ClientError

class text2image:
    
    """
     A class for generating the images based on the prompts 
     
     This class initializes a boto3 session to interact with AWS S3 services and provides
     a method to generate the image
     
     Methods :
        __init__(): Initializes the text2image class by creating the boto3 client
        
        generate_image(prompt: str,cfg_scale=10, steps=50): generate the image based on the prompt
        
         Args:
            prompt (str)         : A prompt passed as an argument to the model
            
            cfg_scale (int)      : Guidance scale is a parameter that controls how much the image generation 
                                   process follows the text prompt. The higher the value, the more the image
                                   sticks to a given text input and vice-versa. It ranges from (1-20)
                             
            inference_steps (int): Inference steps controls how many steps will be taken during this process. 
                                   The higher the value, the more steps that are taken to produce the image
                                   It ranges from (5-100).
         Returns:
            An Image will be generated and saved to the local directory
    """
    
    def __init__(self):
        #Initialization of boto3 client object
        self.client = boto3.client('bedrock-runtime')
        
    def generate_image(self,prompt: str,cfg_scale=10, inference_steps=50):
        # Default Argument values of cfg_scale and inference_steps are passed to the method
        # User can also pass their own arguments while calling the method
        try:
            # Initialize the body variable with arguments passed to the method
            body = json.dumps({
                        "text_prompts": [{"text": prompt}],
                        "seed": 10,
                        "cfg_scale": cfg_scale,
                        "steps": inference_steps,
                    })
            # Generates the image by passing the model_name, body.. to the invoke_model method 
            response = self.client.invoke_model(
                        modelId="stability.stable-diffusion-xl-v1",
                        accept = "application/json",
                        contentType="application/json",
                        body=body
                    )   
            response_body = json.loads(response.get("body").read())
            base64_image = response_body.get("artifacts")[0].get("base64")
            # Encodes the string stored in base64_image into bytes using ASCII encoding.
            base64_bytes = base64_image.encode('ascii')
            # base64 encoded data stored in base64_bytes is decoded back into its original byte representation
            image_bytes = base64.b64decode(base64_bytes)
            image = Image.open(io.BytesIO(image_bytes))
            # Result image will be stored to local directory
            image.save("./image.jpg") 
            # Image path will be printed
            print("image saved to path :  /image.jpg")
        except ClientError as e:
            # Logs the error if the error related to the client
            logging.error("A client error occured: %s", e)
            return None 
    
         