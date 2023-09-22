from dotenv import dotenv_values, load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import (OnlinePDFLoader, PyPDFLoader,
                                        UnstructuredFileLoader)
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter

# This will (likely) generate mock interview questions based on the jobspec
# and the resume. The resume is a PDF and the spec is
# in text format. You will need to change the loaders appropriately
# to get them from their locations.

# externalize the configuration into a ".env" file. In particular, 
# OPENAI_API_KEY={key value}
# should be set in the .env file
config = dotenv_values(".env")



def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f'Spent a total of {cb.total_tokens} tokens')

    return result

def main():
    # gpt-3.5-turbo is rate-limited. Apparently, better than 'text-davinci-003'
    # but since I am not (yet) paying for OPENAI API access, I get a lot of
    # rate-limited exceptions. However, since I am using langchain, and 
    # chat chains, I can't use davinci here (well, not easily)

    # two llms, one for the summary (that specs max_tokens) and one
    # for the generation. I found that this arrangement works best
    # to not overrun the buffer size
    llm_summarize = ChatOpenAI(
        model_name = "gpt-3.5-turbo",
        temperature=0.05,
        openai_api_key=config["OPENAI_API_KEY"],
        max_tokens=1000
    )

    llm_generate = ChatOpenAI(
        model_name = "gpt-3.5-turbo",
        temperature=0.05,
        openai_api_key=config["OPENAI_API_KEY"],
    )



    #loader = OnlinePDFLoader("https://tworavens.ai/schneeman-brent-resume.pdf")
    loader = PyPDFLoader("./schneeman-brent-resume.pdf")

    the_resume = loader.load()

    text_loader = UnstructuredFileLoader("./job-spec.txt")

    the_spec = text_loader.load()

    # splitting the spec into chunks to summarize.
    # using a 1000 token chunk size (with the default overlap)
    # of 200 tokens) to attempt to extract specifics while 
    # maintaining overall context. This is 100% a guess
    text_splitter = CharacterTextSplitter(chunk_size=1500) 
    the_spec_chunks = text_splitter.split_text(the_spec[0].page_content)

    docs = [Document(page_content=t) for t in the_spec_chunks]

    # Summarize the spec. This is mostly to reduce the token size of the 
    # spec to something that can fit into the "generate the cover letter"
    # prompt. If the spec is short enough, it could be used directly.

    # this can be "map_reduce", "refine", or "stuff" - not sure which is 'best'
    chain_summarize = load_summarize_chain(llm_summarize, "refine")

    summarized_spec = chain_summarize.run(docs)
    print(summarized_spec)

    questions = generate_cover(llm_generate, the_resume, summarized_spec)
    print(questions)

    # dump it out into a file
    with open('questions.txt', 'w') as f:
        f.writelines(questions)

def generate_cover(llm_generate, the_resume, summarized_spec):
    prompt_template = """You are the hiring manager for the jobspec below. You have
    a technical machine learning background and are interviewing the candidate represented
    by the resume. Based on the jobspec and resume content, assess the candidate's qualifications and 
    generate mock interview questions focusing on their relevant experience and skills for the role.
    Provide ten interview questions as a number list.
        Jobspec: {jobspec}
        Resume: {resume}
        Interview Questions:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["jobspec", "resume"]
    )

    # generate the cover letter. NOTE: you will need to proofread the cover because
    # it will asssert qualifications not present in the resume (e.g. I apparently 
    # have multiple PhDs...).

    chain = LLMChain(llm=llm_generate, prompt=PROMPT)
    mock_interview = chain.apply([{"jobspec": summarized_spec, "resume": the_resume[0].page_content}])
    questions = mock_interview[0]["text"]
    return questions


if __name__ == "__main__":
    main()