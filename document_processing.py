# document_processing.py

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
import tiktoken


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def process_resume(resume, llm_summarize):
    resume_tokens = num_tokens_from_string(resume, "cl100k_base")
    print("Resume tokens: ", resume_tokens)

    if(resume_tokens > 3300):
        # Process resume
        splitter = CharacterTextSplitter(chunk_size=200)
        resume_chunks = splitter.split_text(resume)
        resume_docs = [Document(page_content=chunk) for chunk in resume_chunks]

        # Summarize resume
        summarize_chain = load_summarize_chain(llm_summarize, "refine")
        resume = summarize_chain.run(resume_docs)
        print("Summarized resume tokens: ", num_tokens_from_string(resume, "cl100k_base"))
    return resume


def process_spec(job_spec, llm_summarize):
    spec_tokens = num_tokens_from_string(job_spec, "cl100k_base")
    print("Jobspec tokens: ", spec_tokens)
    if(spec_tokens > 450):
        # Process job spec
        splitter = CharacterTextSplitter(chunk_size=200)
        spec_chunks = splitter.split_text(job_spec)
        spec_docs = [Document(page_content=chunk) for chunk in spec_chunks]

        # Summarize spec
        summarize_chain = load_summarize_chain(llm_summarize, "refine")
        job_spec = summarize_chain.run(spec_docs)
        print("Summarized spec tokens: ", num_tokens_from_string(job_spec, "cl100k_base"))
    return job_spec