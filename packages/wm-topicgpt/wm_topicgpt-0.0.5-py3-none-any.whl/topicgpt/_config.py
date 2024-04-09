from dataclasses import dataclass


@dataclass
class Config:
    
    # LLM configurations
    consumer_id: str = None
    private_key_path: str = None
    mso_llm_env: str = None

    # Azure PII filter
    azure_key: str = None
    azure_endpoint: str = None