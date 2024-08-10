from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    bot_token_pro: str
    send_message_url: str
    send_photo_url: str
    database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloud_name: str
    cloud_api_key: str
    cloud_api_secret: str
    resto_login: str
    resto_password: str
    resto_url: str
    resto_auth_url: str
    resto_storage_url: str
    resto_nomenclature_url: str
    resto_products_url: str
    google_client_id: str
    google_client_secret: str
    api_secret_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()