from dotenv import load_dotenv
import boto3
import json
import time
import csv
import openai
from dotenv import load_dotenv
import os
import numpy as np
from datetime import datetime
from llama_cpp import Llama

from langchain import hub
from langchain.agents import load_tools,AgentExecutor, create_react_agent
from langchain.llms.bedrock import Bedrock


try:
    from module.prompt_hub import local_hub_pull
except:
    from prompt_hub import local_hub_pull

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class BedrockInvoker:
    """
    AWS Bedrock Runtime을 사용하여 모델을 호출하기 위한 기본 클래스입니다.
    AWS의 Bedrock 서비스와 연동하여 모델을 호출하는 데 필요한 공통 속성과 메서드를 정의합니다.
    """
    def __init__(self):
        self.region_name = 'us-east-1'
        self.runtime_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region_name,
            ) 
        self.content_type = 'application/json'
        self.accept = 'application/json'

class ChatModelInvoker(BedrockInvoker):
    """
    Bedrock 기반의 챗봇 모델을 호출하여 대화 응답을 생성하는 클래스입니다.
    사용자의 질문에 대한 모델의 응답을 생성하는 메서드를 포함합니다.
    """    
    def __init__(self):
        super().__init__()  
        self.model_name = 'anthropic.claude-instant-v1'
        # self.model_name = 'anthropic.claude-v2:1'
        self.prompt_intro = "\n\nHuman:"
        self.response_intro = "\n\nAssistant:"

    def generate_response(self, question, max_tokens=500, temperature=0, top_p=0.9):
        """
        질문에 대한 모델의 응답을 생성합니다.
        Args:
            question (str): 사용자로부터 받은 질문.
            max_tokens (int): 생성할 최대 토큰 수.
            temperature (float): 샘플링 온도.
            top_p (float): 토큰 샘플링에 사용되는 확률의 상위 퍼센트.
        Returns:
            dict: 모델이 생성한 응답을 담은 딕셔너리.
        """
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
    
    def ReAct(self,prompt):
        prompt_hub = hub.pull("hwchase17/react")
        llm = Bedrock(
        model_id=self.model_name, 
        client=self.runtime_client, 
        streaming=False)
        tools = load_tools([ "llm-math",'wikipedia'] ,llm=llm)

        agent  = create_react_agent(llm, tools, prompt_hub)

        agent_executor = AgentExecutor(agent=agent, tools=tools,handle_parsing_errors=True)
        ans = agent_executor.invoke({"input": prompt})
        return ans

    def custom_prompt_set(self,prompt,prompt_nm):
        prompt_hub =  local_hub_pull(prompt_nm)
        llm = Bedrock(
        model_id=self.model_name, 
        client=self.runtime_client, 
        streaming=False)
        tools = load_tools([] ,llm=llm)
        agent  = create_react_agent(llm, tools, prompt_hub)
        agent_executor = AgentExecutor(agent=agent, tools=tools,handle_parsing_errors=True)
        ans = agent_executor.invoke({"input": prompt})
        return ans

class EmbeddingInvoker(BedrockInvoker):
    """
    텍스트 임베딩을 생성하기 위한 클래스입니다.
    다양한 임베딩 모델을 호출하여 텍스트 데이터에 대한 벡터 임베딩을 생성하는 메서드를 포함합니다.
    """    
    def __init__(self):
        super().__init__()

    def coher_embedding(self, prompt):
        """
        Cohere 모델을 사용하여 주어진 텍스트 프롬프트에 대한 임베딩을 생성합니다.
        Args:
            prompt (str): 임베딩을 생성할 텍스트 프롬프트.
        Returns:
            numpy.ndarray: 생성된 임베딩 벡터.
        """        
        cohereModelId = 'cohere.embed-multilingual-v3'

        # Ensure that the prompt is always a list of strings
        if not isinstance(prompt, list):
            prompt = [prompt]  # Convert a single string prompt to a list

        coherePayload = json.dumps({
            'texts': prompt,
            'input_type': 'search_document',
            'truncate': 'NONE'
        })

        print("\nInvoking Cohere Embed...")
        response = self.runtime_client.invoke_model(
            body=coherePayload, 
            modelId=cohereModelId, 
            accept=self.accept, 
            contentType=self.content_type
        )

        body = response.get('body').read().decode('utf-8')
        response_body = json.loads(body)
        return_val = np.array(response_body['embeddings'])[0]
        return return_val
        
    def generate_embeddings(self, body):
        """
        Amazon Titan Embeddings G1 모델을 사용하여 주어진 텍스트에 대한 임베딩을 생성합니다.
        Args:
            body (str): 요청 본문.
        Returns:
            dict: 생성된 임베딩을 포함하는 응답 본문.
        """


        model_id = "amazon.titan-embed-text-v1"

        response = self.runtime_client.invoke_model(
            body=body, modelId=model_id, accept=self.accept, contentType=self.content_type
        )

        response_body = json.loads(response.get('body').read())

        return response_body

    def amazon_g1_embedding(self,prompt):
        """
        주어진 텍스트 프롬프트에 대한 Amazon G1 임베딩을 생성합니다.
        Args:
            prompt (str): 임베딩을 생성할 텍스트 프롬프트.
        Returns:
            numpy.ndarray: 생성된 임베딩 벡터.
        """        
        body = json.dumps({
        "inputText": prompt,
    })
        response = self.generate_embeddings(body)
        embedding_res = response['embedding']
        return_val = np.array(embedding_res)
        return return_val

    def cosine_similarity(self,A,B):
        """
        두 벡터 간의 코사인 유사도를 계산합니다.
        Args:
            A (numpy.ndarray): 첫 번째 벡터.
            B (numpy.ndarray): 두 번째 벡터.
        Returns:
            float: 두 벡터 간의 코사인 유사도.
        """        
        return np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))



class ChatGPTAPIResponder:
    """
    OpenAI의 ChatGPT API를 사용하여 텍스트 응답을 생성하는 클래스입니다.
    사용자의 프롬프트에 대한 응답을 생성하는 메서드를 포함합니다.
    """    
    def __init__(self):
        self.api_key = openai.api_key

    def get_response(self, prompt, engine="gpt-3.5-turbo", max_tokens=250, temperature=0.5):
        """
        주어진 프롬프트에 대한 응답을 생성합니다.
        Args:
            prompt (str): 사용자로부터 받은 프롬프트.
            engine (str): 사용할 OpenAI 엔진.
            max_tokens (int): 생성할 최대 토큰 수.
            temperature (float): 샘플링 온도.
        Returns:
            list: 모델이 생성한 응답 메시지를 포함하는 리스트.
        """        
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
    """
    phi2 모델을 사용하여 텍스트 응답을 생성하는 클래스입니다.
    사용자의 질문에 대한 응답을 생성하는 메서드를 포함합니다.
    """    
    def __init__(self) -> None:
        self.llm = Llama(
        model_path="model/phi-2.Q6_K.gguf",
        chat_format="phind")
        pass

    def get_response(self, question):
        """
        주어진 질문에 대한 응답을 생성합니다.
        Args:
            question (str): 사용자로부터 받은 질문.
        Returns:
            str: 모델이 생성한 응답.
        """
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
        for choice in answer['choices']:
            message = choice['message']
            if message['role'] == 'assistant':
                return message['content']

if __name__ == '__main__':
    # q = "아인슈타인이 중력 상수를 왜 거부했는 지 논리적으로 생각해보고, 나중에 어떻게 받아들였을 지 생각해봐."
    q = "오늘 진짜 너무 행복한 날이야. 내가 오늘 왜 행복하게?"
    test_react_ins = ChatModelInvoker()
