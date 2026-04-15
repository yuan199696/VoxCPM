"""API configuration"""

from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API settings"""

    host: str = "0.0.0.0"
    port: int = 8000
    model_id: str = "openbmb/VoxCPM2"
    device: str = "auto"
    max_text_length: int = 1000
    lazy_load: bool = True
    default_output_format: str = "file"

    class Config:
        env_prefix = "VOXCPM_API_"
