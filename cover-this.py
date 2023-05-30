from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.document_loaders import OnlinePDFLoader
from langchain.document_loaders import UnstructuredFileLoader

import os

os.environ["OPENAI_API_KEY"] = ""

llm = OpenAI(
    model_name = "text-davinci-003",
    temperature=0.0,
    max_tokens=-1,
    openai_api_key=""
)

#llm = ChatOpenAI(temperature=0.0)
#llm = OpenAI(openai_api_key="")

loader = OnlinePDFLoader("https://tworavens.ai/schneeman-brent-resume.pdf")

the_resume = loader.load()[0].page_content

text_loader = UnstructuredFileLoader("./job-spec.txt")

the_spec = text_loader.load()[0].page_content

# the final request must be less than 4097 tokens, so summarize the resume

summarize_template = """
Summarize {resume} to less than 3500 tokens
"""
prompt = PromptTemplate(
    input_variables=["resume"],
    template=summarize_template
)
summarized_resume = llm(prompt.format(resume=the_resume))

summarized_spec_template = """
Summarize {spec} to less than 2000 tokens. Extract the key 
requirements from spec and include in summary
"""
prompt = PromptTemplate(
    input_variables=["spec"],
    template=summarized_spec_template
)
summarized_spec = llm(prompt.format(spec=the_spec))


cover_prompt_template = """
### Resume ###
{resume}
### Job posting ###
{posting} 

Write a cover letter for the job posting. 
Only use supporting examples from the resume and be exact.
Be professional and emphasize leadership experience, and ensure
to use less than 1000 words. 
"""

cover_letter = PromptTemplate(
    input_variables=["resume","posting"],
    template=cover_prompt_template
)

prompt = PromptTemplate(
    input_variables=["resume","posting"],
    template="### Resume ###{resume}### Job posting ###{posting}\nIs the resume qualified for the job posting? provide details"
)

cover = (llm(cover_letter.format(resume=the_resume, posting=summarized_spec)))


with open('cover-letter.txt', 'w') as f:
    f.writelines(cover)

print(cover)