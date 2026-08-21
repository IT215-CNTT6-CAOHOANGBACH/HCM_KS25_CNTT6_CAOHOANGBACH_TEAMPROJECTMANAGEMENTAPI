from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str ="TEAM PROJECT MANAGEMENT API"
    APP_VERSION: str ="1.0.0"
    APP_DESCRIPTION:str ="úng dụng quản lí"
    
    DATABASE_URL:str
    
    SECRET_KEY:str
    
    ALGORITHM:str ="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int =60
    
    ALLOWED_ORIGINS:list[str] = ["http://localhost:3000"]
    
    class Config:
        
        env_file =".env"
        env_file_encoding ="utf-8"
        
        
settings = Settings()
       