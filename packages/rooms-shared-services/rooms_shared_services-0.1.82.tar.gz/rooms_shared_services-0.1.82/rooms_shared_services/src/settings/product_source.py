from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="product_source_")

    tablename: str
    region_name: str = "us-east-1"
    sku_indexname: str
    original_ident_indexname: str
    ident_code: str
    ident_key: str
