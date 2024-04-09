from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
)
import logging
import aiohttp
import requests
from pydantic.v1 import Field, root_validator
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (
    BaseMessage,
    ChatResult,
)
from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
)
logger = logging.getLogger(__name__)


class WalmartAzureOpenAiChatModels(ChatOpenAI):

    model_name: Optional[str]
    vendor: str
    task: Optional[str]
    api_version: Optional[str]
    instance_name: Optional[str]
    deployment_name: Optional[str]
    trproduct_id: Optional[str]
    consumer_id: Optional[str]
    consumer_timestamp: Optional[str]
    consumer_key_version: Optional[str]
    consumer_auth_signature: Optional[str]
    svc_env: Optional[str]
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Configuration for this pydantic object."""

        extra = "allow"
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def build_model_kwargs(cls, values: Dict) -> Dict:
        """Build model_kwargs"""
        all_required_field_names = {
            'consumer_id',
            'consumer_auth_signature',
            'task',
            'deployment_name',
            'api_version',
            'consumer_timestamp',
            'trproduct_id',
            'model_kwargs',
            'model_name',
            'svc_env',
            'consumer_key_version',
            'instance_name',
            'vendor',
        }

        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name not in all_required_field_names:
                if field_name in extra:
                    raise ValueError(f"Found {field_name} supplied twice.")
                extra[field_name] = values.pop(field_name)
        values["model_kwargs"] = extra
        return values
    
    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that consumer details are present."""

        if not values["model_name"] and not values["instance_name"]:
            raise ValueError("Either model_name or instance_name needs to be provided.")
        if not values["consumer_id"]:
            raise ValueError("Missing mandatory parameter consumer_id.")
        if not values["svc_env"]:
            raise ValueError("Missing mandatory parameter svc_env.")

        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")
        return values

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "azureopenai-chat-models"
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = await _acompletion_with_retry(
            self, messages=message_dicts, run_manager=run_manager, **params
        )
        return self._create_chat_result(response)
    
    def completion_with_retry(self, **kwargs: Any) -> Any:
        _model_kwargs = self.model_kwargs or {}
        payload = {}

        if self.instance_name:
            payload["instance"] = self.instance_name
        if self.model_name:
            payload["model"] = self.model_name
        if self.api_version:
            payload["api-version"] = self.api_version
        if self.deployment_name:
            payload["deployment-name"] = self.deployment_name

        payload["task"] = "chat/completions"
        # HTTP headers for authorization

        model_params = {
            "messages": kwargs["messages"],
        }
        model_params.update(_model_kwargs)
        payload["model-params"] = model_params

        headers = {
            "Content-Type": "application/json",
            "WM_CONSUMER.ID": self.consumer_id,
            "WM_SVC.NAME": "WMTLLMGATEWAY",
            "WM_SVC.ENV": self.svc_env,
        }

        if self.consumer_timestamp != "":
            headers["WM_CONSUMER.INTIMESTAMP"] = self.consumer_timestamp
        if self.consumer_key_version != "":
            headers["WM_SEC.KEY_VERSION"] = self.consumer_key_version
        if self.consumer_auth_signature != "":
            headers["WM_SEC.AUTH_SIGNATURE"] = self.consumer_auth_signature
        if self.trproduct_id != "":
            headers["WM_TR_PRODUCT.ID"] = self.trproduct_id

        gateway_endpoint = (
            f"https://wmtllmgateway.{self.svc_env}.walmart.com/wmtllmgateway/v1/openai"
        )

        def _make_rest_call(endpoint: str, headers: dict, payload: dict):
            try:
                response = requests.post(endpoint, headers=headers, json=payload, verify=False)
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error raised by inference endpoint: {e}")

            if response.status_code != 200:
                print(response.status_code)
                raise ValueError(f"Error raised by inference API: {response.content}")
            return response.json()

        # send request
        generated_text = _make_rest_call(gateway_endpoint, headers, payload)
        return generated_text
    

async def _acompletion_with_retry(llm, **kwargs: Any) -> Any:
    _model_kwargs = llm.model_kwargs or {}
    payload = {}

    if llm.instance_name:
        payload["instance"] = llm.instance_name
    if llm.model_name:
        payload["model"] = llm.model_name
    if llm.api_version:
        payload["api-version"] = llm.api_version
    if llm.deployment_name:
        payload["deployment-name"] = llm.deployment_name

    payload["task"] = "chat/completions"
    # HTTP headers for authorization

    model_params = {
        "messages": kwargs["messages"],
#         "response_format": {"type": "json_object"}
    }
    model_params.update(_model_kwargs)
    payload["model-params"] = model_params

    headers = {
        "Content-Type": "application/json",
        "WM_CONSUMER.ID": llm.consumer_id,
        "WM_SVC.NAME": "WMTLLMGATEWAY",
        "WM_SVC.ENV": llm.svc_env,
    }

    if llm.consumer_timestamp != "":
        headers["WM_CONSUMER.INTIMESTAMP"] = llm.consumer_timestamp
    if llm.consumer_key_version != "":
        headers["WM_SEC.KEY_VERSION"] = llm.consumer_key_version
    if llm.consumer_auth_signature != "":
        headers["WM_SEC.AUTH_SIGNATURE"] = llm.consumer_auth_signature
    if llm.trproduct_id != "":
        headers["WM_TR_PRODUCT.ID"] = ""  # llm.trproduct_id

    gateway_endpoint = (
        f"https://wmtllmgateway.{llm.svc_env}.walmart.com/wmtllmgateway/v1/openai"
    )

    async def _amake_rest_call(endpoint: str, headers: dict, payload: dict):
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False),
            timeout=aiohttp.ClientTimeout(total=None, sock_connect=120, sock_read=120),
        ) as session:
            try:
                async with session.post(
                    endpoint, headers=headers, json=payload
                ) as response:
                    default_result = {
                        'choices': [{'finish_reason': 'stop', 'index': 0, 'message': {'content': '', 'role': 'assistant'}}], 
                        'created': 1709962264, 'id': '', 'model': '', 'object': '', 'system_fingerprint': None, 
                        'usage': {'completion_tokens': 0, 'prompt_tokens': 0, 'total_tokens': 0},
                        'error': ''
                    }
                    if response.status != 200:
                        print(f'Error raised by inference API: {await response.text()}')
                        result = default_result
                        result['error'] = f'Error raised by inference API: {await response.text()}'
                        # raise ValueError(f'Error raised by inference API: {await response.text()}')
                    else:
                        if 'application/json' in response.headers.get('Content-Type', ''):
                            result = await response.json()
                        else:
                            print('Error: response is not in JSON')
                            result = default_result
                            result['error'] = f'Error raised by parsing response to JSON'
                            # raise ValueError(f'Error raised by parsing response to JSON')
                    return result
            except aiohttp.ClientError as e:
                raise ValueError(f"Error raised by inference endpoint: {e}")

    # send request
    generated_texts = _amake_rest_call(gateway_endpoint, headers, payload)
    return await generated_texts