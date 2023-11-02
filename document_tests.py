from document_processing import num_tokens_from_string, remove_stop_words
from pdf_utils import extract_text_from_pdf
from langchain.document_loaders import (UnstructuredFileLoader)


def main():
    # gpt-3.5-turbo is rate-limited. Apparently, better than 'text-davinci-003'
    # but since I am not (yet) paying for OPENAI API access, I get a lot of
    # rate-limited exceptions. However, since I am using langchain, and 
    # chat chains, I can't use davinci here (well, not easily)

    #loader = OnlinePDFLoader("https://tworavens.ai/schneeman-brent-resume.pdf")
    the_resume = extract_text_from_pdf("./schneeman-brent-resume.pdf" )

    text_loader = UnstructuredFileLoader("./job-spec.txt")

    job_spec = text_loader.load()
    the_job_spec = job_spec[0].page_content

    resume_tokens = num_tokens_from_string(the_resume, "cl100k_base")
    print("Resume tokens: ", resume_tokens)

    filtered_resume = remove_stop_words(the_resume)
    print("Filtered resume tokens: ", num_tokens_from_string(filtered_resume, "cl100k_base"))

    spec_tokens = num_tokens_from_string(the_job_spec, "cl100k_base")
    print("Spec tokens: ", spec_tokens)
    filtered_spec = remove_stop_words(the_job_spec)
    print("Filtered spec tokens: ", num_tokens_from_string(filtered_spec, "cl100k_base"))

if __name__ == "__main__":
    main()