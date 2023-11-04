from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatGooglePalm
import streamlit as st

class LLMFactory:

    llm_provider: str = None

    def __init__(self):
        self.llm_provider = st.secrets["llm_configuration"]["LLM_PROVIDER"]
        if(self.llm_provider == "OPENAI"):
            self.api_key = st.secrets["llm_configuration"]["OPENAI_API_KEY"]                                                           
        elif(self.llm_provider == "GOOGLE"):
            self.api_key = st.secrets["llm_configuration"]["GOOGLE_API_KEY"]
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
