from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    model_name: str = "deepseek-chat"
    data_dir: str = "./data"
    max_chunk_size: int = 1200
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    max_tokens: int = 4096
    temperature: float = 0.7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "protected_namespaces": (),
    }

    def get_data_path(self, *parts: str) -> Path:
        p = Path(self.data_dir, *parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
