from dotenv import load_dotenv
import boto3
import json
import time
import csv
import openai
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatModelInvoker:
    def __init__(self):
        self.region_name = 'us-east-1'
        self.runtime_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region_name,
            )
        self.model_name = 'anthropic.claude-instant-v1'
        self.content_type = 'application/json'
        self.accept = 'application/json'
        self.prompt_intro = "\n\nHuman:"
        self.response_intro = "\n\nAssistant:"

    def generate_response(self, question, max_tokens=500, temperature=0, top_p=0.9):
        prompt = self.prompt_intro + question + self.response_intro
        request_body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        })

        response = self.runtime_client.invoke_model(
            body=request_body, 
            modelId=self.model_name, 
            accept=self.accept, 
            contentType=self.content_type)
        response_body = json.loads(response.get('body').read())

        return response_body.get('completion')

class ChatGPTAPIResponder:
    def __init__(self):
        self.api_key = openai.api_key

    def get_response(self, review, engine="gpt-3.5-turbo", max_tokens=250, temperature=0.5):
        start_time = datetime.now()  
        examples = self._get_formatted_examples()
        prompt = self._generate_prompt(review, examples)
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[{"role": "system", "content": "Analyze the following review and provide a structured analysis."},
                      {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        end_time = datetime.now() 
        analysis = response['choices'][0]['message']['content'].strip().split("\n")
        result = tuple(line.split(": ")[1] for line in analysis if ": " in line)
        return (*result, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))
