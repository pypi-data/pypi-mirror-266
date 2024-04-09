import warnings
warnings.filterwarnings("ignore")
import os
import time
import math
import asyncio
from tqdm import tqdm
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
)
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from base64 import b64encode
from langchain.schema import HumanMessage
from topicgpt.walmart_llm._chat_model import WalmartAzureOpenAiChatModels
from topicgpt.walmart_llm._embed_model import WalmartAzureOpenaiEmbeddings
from topicgpt import config


def test_config():
    if config.consumer_id is None:
        raise ValueError("Please set up config.consumer_id!")
    if config.private_key_path is None:
        raise ValueError("Please set up config.private_key_path!")
    if config.mso_llm_env is None:
        raise ValueError("Please set up config.mso_llm_env!")

test_config()
os.environ['OPENAI_API_KEY'] = config.consumer_id

def get_timestamp() -> int:
    """Create timestamp
    Returns:
        int: timestamp
    """
    return int(time.time()) * 1000
 
def sign_data(private_key: str, data: str) -> bytes:
    """Create authorization signature
    Args:
        private_key (str): Path to private key
        data (str): Additional information needed to generate key in format:
            consumer_id
            timestamp
            key version
    Returns:
        bytes: authorization signature
    """
    key = open(private_key, "r").read()
    rsakey = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(data.encode("utf-8"))
    sign = signer.sign(digest)
    return b64encode(sign)
 
def generate_auth_sig(consumer_id: str, private_key_path: str, key_version: str = "1"):
    """_summary_
    Args:
        consumer_id (str): Service App. consumer ID
        private_key_path (str): private key path
        key_version (str) , Defaults to "1" : SOA key version
    Returns:
        tuple: epoch_time, auth_signature
    """
    epoch_time = get_timestamp()
    data = f"{consumer_id}\n{epoch_time}\n{key_version}\n"
    auth_signature = sign_data(private_key_path, data).decode()
    return epoch_time, auth_signature

def instantiate_walmart_chat_completion(model_version="gpt-35-turbo", temperature=0.):
    """The helper function that calls LLM gateway LLM
    Args:
        temperature (_type_): _description_
        max_tokens (_type_): _description_
        top_p (_type_): _description_
        presence_penalty (_type_): _description_
        frequency_penalty (_type_): _description_
        model_version (str): LLM model version
    Returns:
        _type_: _description_
    """
    epoch_ts, auth_sig = generate_auth_sig(config.consumer_id, config.private_key_path)
    consumer_params = {
        "consumer_id": config.consumer_id,
        "consumer_timestamp": str(epoch_ts),
        "consumer_key_version": "1",
        "consumer_auth_signature": auth_sig,
        "svc_env": config.mso_llm_env,
    }
    chat_client = WalmartAzureOpenAiChatModels(
        vendor="azure-openai",
        task="chat/completions",
        model_name=model_version,
        temperature=temperature,
        **consumer_params,
    )
    return chat_client

def instantiate_walmart_embedding(model_version="text-embedding-ada-002"):
    epoch_ts, auth_sig = generate_auth_sig(config.consumer_id, config.private_key_path)
    consumer_params = {
        "consumer_id": config.consumer_id,
        "consumer_timestamp": str(epoch_ts),
        "consumer_key_version": "1",
        "consumer_auth_signature": auth_sig,
        "svc_env": config.mso_llm_env,
    }
    embedding_client = WalmartAzureOpenaiEmbeddings(vendor="azure-openai", model_name=model_version, **consumer_params)
    return embedding_client


class ChatModel:

    def __init__(self, model_name="gpt-35-turbo", temperature=0., batch_size=500):
        self.temperature = temperature
        self.model = instantiate_walmart_chat_completion(model_version=model_name, temperature=temperature)
        self.batch_size = batch_size

    def completion(self, message):
        message = [[HumanMessage(content=message)]]
        response = self.model.generate(message).generations[0][0].text
        return response

    @retry(stop=stop_after_attempt(10))
    def retry_completion(self, message):
        if self.temperature == 0.:
            raise ValueError(f"To add some uncertainty, please do not set `temperature=0.`")
        try:
            message = [[HumanMessage(content=message)]]
            response = self.model.generate(message).generations[0][0].text
            return response
        except Exception as e:
            raise ValueError(f"{e}")
        
    @retry(stop=stop_after_attempt(10))
    def retry_json_completeion(self, message, keys):
        if self.temperature == 0.:
            raise ValueError(f"To add some uncertainty, please do not set `temperature=0.`")
        try:
            message = [[HumanMessage(content=message)]]
            response = self.model.generate(message).generations[0][0].text
            json_response = eval(response)
            for key in keys:
                if key not in json_response:
                    raise ValueError(f"Response doesn't include {key}")
            return json_response
        except Exception as e:
            raise ValueError(f"{e} - Response: {json_response}")
    
    def batch_completion(self, messages):
        
        async def agenerate(model, messages):
            responses = await model.agenerate(messages)
            return responses.generations

        responses = []
        num_batch = math.ceil(len(messages) / self.batch_size)
        for idx in tqdm(range(0, len(messages), self.batch_size), total=num_batch):
            batch_messages = [[HumanMessage(content=message)] for message in messages[idx: idx+self.batch_size]]
            batch_responses = asyncio.run(agenerate(self.model, batch_messages))
            responses.extend([response[0].text for response in batch_responses])
        return responses


class AdaEmbedModel:

    def __init__(self, batch_size=500, model_name="text-embedding-ada-002"):
        self.model = instantiate_walmart_embedding(model_version=model_name)
        self.batch_size = batch_size

    @retry(wait=wait_exponential(multiplier=1, min=2, max=60))
    def retry_embed_documents(self, documents):
        return self.model.embed_documents(documents)

    def embed_documents(self, documents):
        embeddings = []
        num_batch = math.ceil(len(documents) / self.batch_size)
        for idx in tqdm(range(0, len(documents), self.batch_size), total=num_batch):
            batch_documents = documents[idx: idx+self.batch_size]
            batch_embeddings = self.retry_embed_documents(batch_documents)
            embeddings.extend(batch_embeddings)
        return embeddings
    
    def embed_query(self, document):
        return self.model.embed_query(document)