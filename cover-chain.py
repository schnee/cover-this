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

# This will (likely) generate a cover letter based on a Resume
# and a job specification. The resume is a PDF and the spec is
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

    cover_txt = generate_cover(llm_generate, the_resume, summarized_spec)
    print(cover_txt)

    # dump it out into a file
    with open('cover-letter.txt', 'w') as f:
        f.writelines(cover_txt)

def generate_cover(llm_generate, the_resume, summarized_spec):
    prompt_template = """Use the jobspec below to write a cover letter based on
    the resume, and do not assert experience that is not in the resume. 
    Be professional, and emphasize leadership experience mentioned in the resume.
        Jobspec: {jobspec}
        Resume: {resume}
        Cover letter:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["jobspec", "resume"]
    )

    # generate the cover letter. NOTE: you will need to proofread the cover because
    # it will asssert qualifications not present in the resume (e.g. I apparently 
    # have multiple PhDs...).

    chain = LLMChain(llm=llm_generate, prompt=PROMPT)
    cover_letter = chain.apply([{"jobspec": summarized_spec, "resume": the_resume[0].page_content}])
    cover_txt = cover_letter[0]["text"]
    return cover_txt


if __name__ == "__main__":
    main()