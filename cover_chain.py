from langchain.chains import LLMChain
from langchain.document_loaders import (UnstructuredFileLoader)
from langchain.prompts import PromptTemplate
import document_processing

from llmfactory import LLMFactory
from pdf_utils import extract_text_from_pdf

# This will (likely) generate a cover letter based on a Resume
# and a job specification. The resume is a PDF and the spec is
# in text format. You will need to change the loaders appropriately
# to get them from their locations.


def generate_cover_letter(resume, job_spec):

    # two llms, one for the summary (that specs max_tokens) and one
    # for the generation. I found that this arrangement works best
    # to not overrun the buffer size

    factory = LLMFactory()

    llm_summarize = factory.create_summarizer()
    llm_generate = factory.create_generator()

    job_spec = document_processing.process_spec(job_spec, llm_summarize)

    resume = document_processing.process_resume(resume, llm_summarize)

    # Generate cover letter
    cover_letter = generate_cover(llm_generate, resume, job_spec)
    print("Cover letter tokens: ", document_processing.num_tokens_from_string(cover_letter, "cl100k_base"))

    return cover_letter


def main():

    the_resume = extract_text_from_pdf("./schneeman-brent-resume.pdf" )

    text_loader = UnstructuredFileLoader("./job-spec.txt")

    the_spec = text_loader.load()

    cover_txt = generate_cover_letter(the_resume, the_spec[0].page_content)

    print(cover_txt)

    # dump it out into a file
    with open('cover-letter.txt', 'w') as f:
        f.writelines(cover_txt)

def generate_cover(llm_generate, the_resume, summarized_spec):
    prompt_template = """Use the jobspec below to write a cover letter based on
    the resume. Do not claim experience or education that is not in the resume. 
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
    cover_letter = chain.apply([{"jobspec": summarized_spec, "resume": the_resume}])
    cover_txt = cover_letter[0]["text"]
    return cover_txt


if __name__ == "__main__":
    main()