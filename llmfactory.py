from langchain.chat_models import ChatOpenAI
from dotenv import dotenv_values

class LLMFactory:

    llm_provider: str = None

    def __init__(self):
        config = dotenv_values(".env")
        if(config["USE_OPENAI"]):
            self.api_key = config["OPENAI_API_KEY"]
            self.llm_provider = "OPENAI"
        else:
            self.llm_provider = "LOCAL"

    def create_summarizer(self):
        if(self.llm_provider == "OPENAI"): 
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.05,
                openai_api_key=self.api_key,
                max_tokens=1000
            )
        else:
            return None
        
    
    def create_generator(self):
        if(self.llm_provider == "OPENAI"):
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.05,
                openai_api_key=self.api_key
            )
        else:
            return None
