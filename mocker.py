from dotenv import dotenv_values
from langchain.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import UnstructuredFileLoader
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from pdf_utils import extract_text_from_pdf
import pickle
from models import QuestionList

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
    openai_api_key = config["OPENAI_API_KEY"]

    llm_summarize = ChatOpenAI(
        model_name = "gpt-3.5-turbo",
        temperature=0.05,
        openai_api_key=openai_api_key,
        max_tokens=1000
    )

    llm_generate = ChatOpenAI(
        model_name = "gpt-3.5-turbo",
        temperature=0.05,
        openai_api_key=config["OPENAI_API_KEY"],
    )

    #loader = OnlinePDFLoader("https://tworavens.ai/schneeman-brent-resume.pdf")
    the_resume = extract_text_from_pdf("./schneeman-brent-resume.pdf" )

    text_loader = UnstructuredFileLoader("./job-spec.txt")

    the_spec = text_loader.load()

    # splitting the spec into chunks to summarize.
    # using a 1500 token chunk size (with the default overlap)
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

    questions = generate_questions(llm_generate, the_resume, summarized_spec)

    questions_as_json = questions.json(indent=2)

    # dump it out into a file
    with open('questions.txt', 'w') as f:
        f.writelines(questions_as_json)

    # dump as pickle
    with open('questions.pkl', 'wb') as f:
        pickle.dump(questions, f)

def generate_questions(llm_generate, the_resume, summarized_spec):

    output_parser = PydanticOutputParser(pydantic_object=QuestionList)

    format_instructions = output_parser.get_format_instructions()

    prompt_template = """You are the hiring manager for the jobspec below. You have
    a technical machine learning background and are interviewing the candidate represented
    by the resume. Based on the resume and jobspec content, assess the candidate's
    suitability for the role and generate five interview questions focusing on their relevant
    experience and skills for the role. Make sure to ask open-ended questions and 
    question specific experiences in their resume. Ensure that the assessment is written provided
    as if you are speaking directly to the candidate.\n
    
        Resume: {resume}\n

        Jobspec: {jobspec}\n

    {format_instructions}
    """

    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["jobspec", "resume"],
        partial_variables={"format_instructions": format_instructions}
    )

    chain = LLMChain(llm=llm_generate, prompt=PROMPT, output_parser=output_parser)
    resume_content = the_resume#[0].page_content

    # after this, mock_interview is a QuestionList object. That's pretty neat.

    mock_interview = chain.run({"jobspec": summarized_spec, "resume": resume_content})
    
    return mock_interview


if __name__ == "__main__":
    main()