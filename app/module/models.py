from dotenv import load_dotenv
import boto3
import json
import time
import csv
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
from llama_cpp import Llama

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

    def get_response(self, prompt, engine="gpt-3.5-turbo", max_tokens=250, temperature=0.5):
        response = openai.ChatCompletion.create(
            model=engine,
            messages=[{"role": "system", "content": "Analyze the following review and provide a structured analysis."},
                      {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        result = response['choices'][0]['message']['content'].strip().split("\n")
        return result


class phi:
    def __init__(self) -> None:
        self.llm = Llama(
        model_path="model/phi-2.Q6_K.gguf",
        chat_format="phind")
        pass

    def get_response(self, question):
        answer = self.llm.create_chat_completion(
        max_tokens=32,
        stop=["###", "\n\n"],
        messages = [
        {
            "role": "system",
            "content": "당신은 유용한 어시스턴트 입니다. 사용자의 물음에 답하세요.",
        },
          {
              "role": "user",
              "content": question
          }
        ])
        # print(answer)
        # return answer
        for choice in answer['choices']:
            message = choice['message']
            if message['role'] == 'assistant':
                return message['content']

phi_instance = phi()
if __name__== '__main__':
    test = phi()
    q= "Describe the delicous apple."
    print(test.get_response(q))