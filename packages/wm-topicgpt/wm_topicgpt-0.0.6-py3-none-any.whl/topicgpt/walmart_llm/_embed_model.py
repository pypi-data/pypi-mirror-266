from __future__ import annotations

import logging
import os
import requests
from requests.exceptions import SSLError
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    Mapping
)

import numpy as np
from pydantic import BaseModel, model_validator, Field
from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import openai
from langchain_community.embeddings import OpenAIEmbeddings
import tiktoken

logger = logging.getLogger(__name__)

def _embed_with_retry(embeddings: WalmartAzureOpenaiEmbeddings, **kwargs) -> Any:
    payload = {}

    if embeddings.instance_name:
        payload["instance"] = embeddings.instance_name        
    if embeddings.model_name:
        payload["model"] = embeddings.model_name
    if embeddings.api_version:
        payload["api-version"] = embeddings.api_version
    if embeddings.deployment_name:
        payload["deployment-name"] = embeddings.deployment_name
    # HTTP headers for authorization

    payload["task"] = "embeddings"
    model_params = {
        "input": kwargs["input"],
    }
    payload["model-params"] = model_params

    headers = {
        "Content-Type": "application/json",
        "WM_CONSUMER.ID": embeddings.consumer_id,
        "WM_SVC.NAME": "WMTLLMGATEWAY",
        "WM_SVC.ENV": embeddings.svc_env,
    }
    if embeddings.consumer_timestamp != "":
        headers["WM_CONSUMER.INTIMESTAMP"] = embeddings.consumer_timestamp
    if embeddings.consumer_key_version != "":
        headers["WM_SEC.KEY_VERSION"] = embeddings.consumer_key_version
    if embeddings.consumer_auth_signature != "":
        headers["WM_SEC.AUTH_SIGNATURE"] = embeddings.consumer_auth_signature
    if embeddings.trproduct_id != "":
        headers["WM_TR_PRODUCT.ID"] = embeddings.trproduct_id

    endpoint = f"https://wmtllmgateway.{embeddings.svc_env}.walmart.com/wmtllmgateway/v1/openai"

    try:
        try:
            if "REQUEST_CA_BUNDLE" in os.environ:
                response = requests.post(
                    endpoint, headers=headers, json=payload, verify=os.environ.get("REQUEST_CA_BUNDLE")
                )
            else:
                response = requests.post(
                    endpoint, headers=headers, json=payload, verify=True
                )
        except SSLError:
            # print("SSLError. Set REQUEST_CA_BUNDLE to use secure ssl. Falling back to insecure api call.")
            response = requests.post(
                    endpoint, headers=headers, json=payload, verify=False
                )
    except requests.exceptions.RequestException as e:
        print(f"Error raised by inference endpoint: {e}")
        raise ValueError(f"Error raised by inference endpoint: {e}")

    if response.status_code != 200:
        print(f"Error raised by inference API: {response.content}")
        raise ValueError(
            f"Error raised by inference API: {response.content}"
        )
    return response.json()

## override default behaviour
openai.embed_with_retry = _embed_with_retry

class WalmartEmbeddings(BaseModel, Embeddings):

    model_name: Optional[str]
    vendor: str
    task: Optional[str]
    api_version: Optional[str]
    instance_name: Optional[str]
    deployment_name: Optional[str]
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Configuration for this pydantic object."""
        extra = 'allow'
        arbitrary_types_allowed = True
        populate_by_name = True
    
    def __new__(cls, **data: Any):  # type: ignore
        """Initialize the OpenAI object."""
        vendor = data.get("vendor", "")
        if vendor == "azure-openai":
            return WalmartAzureOpenaiEmbeddings(**data)
        return super().__new__(cls)

    @model_validator(mode="before")
    def build_model_kwargs(cls, values: Dict) -> Dict:
        """Build model_kwargs"""
        all_required_field_names = {field.alias for field in cls.__fields__.values()}

        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name not in all_required_field_names:
                if field_name in extra:
                    raise ValueError(f"Found {field_name} supplied twice.")
                extra[field_name] = values.pop(field_name)
        values["model_kwargs"] = extra
        return values

    @model_validator(mode="before")
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that model api_token and endpoint exists in the environment."""
        _vendor = values["vendor"]
        if _vendor not in ["wmt", "azure-openai"]:
            raise ValueError(f"Unsupported vendor {_vendor}.")

        if not values["model_name"]:
            raise ValueError(f"With Walmart (wmt) as vendor, model_name parameter is mandatory.")
        if not values["consumer_id"]:
            raise ValueError("Missing mandatory parameter consumer_id.")
        if not values["svc_env"]:
            raise ValueError("Missing mandatory parameter svc_env.")
        
        return values

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            **{
                "model_name": self.model_name,
                "vendor": self.vendor,
                "task": self.task,
                "api_version": self.api_version,
                "instance_name": self.instance_name,
                "deployment_name": self.deployment_name,
            },
            **{"model_kwargs": self.model_kwargs}
        }

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "walmart-embeddings"
    
    def embed_documents(
        self, texts: List[str], chunk_size: Optional[int] = 0
    ) -> List[List[float]]:
        """Call out to OpenAI's embedding endpoint for embedding search docs.
        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings. If None, will use the chunk size
                specified by the class.
        Returns:
            List of embeddings, one for each text.
        """
        raise NotImplementedError("Embeddings for wmt vendor are not supported.")

    def embed_query(self, text: str) -> List[float]:
        """Call out to OpenAI's embedding endpoint for embedding query text.
        Args:
            text: The text to embed.
        Returns:
            Embedding for the text.
        """
        raise NotImplementedError("Embeddings for wmt vendor are not supported.")
    

class WalmartAzureOpenaiEmbeddings(OpenAIEmbeddings):

    model_name: str = Field(alias="model")
    vendor: str
    api_version: Optional[str]
    instance_name: Optional[str]
    deployment_name: Optional[str]
    consumer_id: Optional[str]
    consumer_timestamp: Optional[str]
    consumer_key_version: Optional[str]
    consumer_auth_signature: Optional[str]
    svc_env: Optional[str]
    trproduct_id: Optional[str]
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Configuration for this pydantic object."""
        extra = 'allow'
        arbitrary_types_allowed = True
        populate_by_name = True

    def validate_environment(cls, values: Dict) -> Dict:
        """Validate parameters"""
        if not values["model_name"]:
            raise ValueError("Missing mandatory parameter model_name.")
        if not values["consumer_id"]:
            raise ValueError("Missing mandatory parameter consumer_id.")
        if not values["svc_env"]:
            raise ValueError("Missing mandatory parameter svc_env.")
        return values

    @property
    def _invocation_params(self) -> Dict:
        azureopenai_args = {
            "model_name": self.model_name,
            "headers": self.headers,
            "instance_name": self.instance_name,
            "deployment_name": self.deployment_name,
            "api_version": self.openai_api_version,
        }
        return azureopenai_args


