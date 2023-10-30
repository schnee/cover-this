from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatGooglePalm
from langchain.llms import GooglePalm
from dotenv import dotenv_values

#pip install google-cloud-aiplatform langchain chromadb pydantic typing-inspect typing_extensions pandas datasets google-api-python-client pypdf faiss-cpu transformers config --upgrade


class LLMFactory:

    llm_provider: str = None

    def __init__(self):
        config = dotenv_values(".env")
        if(config["LLM_TYPE"] == "OPENAI"):
            self.api_key = config["OPENAI_API_KEY"]
            self.llm_provider = "OPENAI"
        elif(config["LLM_TYPE"] == "GOOGLE"):
            self.api_key = config["GOOGLE_API_KEY"]
            self.llm_provider = "GOOGLE"
        else:
            self.llm_provider = "LOCAL"

    def create_summarizer(self):
        if(self.llm_provider == "OPENAI"): 
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.05,
                openai_api_key=self.api_key,
                max_tokens=600
            )
        elif(self.llm_provider == "GOOGLE"):
            return ChatGooglePalm(google_api_key=self.api_key,
                                  max_tokens=1000)
        else:
            return None
        
    
    def create_generator(self):
        if(self.llm_provider == "OPENAI"):
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.05,
                openai_api_key=self.api_key
            )
        elif(self.llm_provider == "GOOGLE"):
            return ChatGooglePalm(google_api_key=self.api_key)
        else:
            return None
