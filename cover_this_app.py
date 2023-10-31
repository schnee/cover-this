import streamlit as st
from cover_chain import generate_cover_letter
from io import StringIO
from io_utils import zip_it
from mocker import assess_and_questions

from pdf_utils import extract_text_from_pdf
from models import QuestionList

# this is the main app

st.title("Cover Letter Generator")

col1, col2 = st.columns(2)

st.markdown("This app will generate a cover letter based on a PDF resume and a job spec. Simply upload the PDF, paste in the jobspec and press the 'Generate' button.")
col1.link_button(":orange[Buy me a coffee]", "https://www.buymeacoffee.com/mahkr",)
#st.markdown("[![Buy me a coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/mahkr)")
col2.link_button("Email me with feedback", "mailto:schneeman@gmail.com")
st.header("Upload Resume")
resume = st.file_uploader("Choose a resume", type=["pdf"])

st.header("Enter Job Spec")  
#job_spec = st.file_uploader("Choose a job spec", type=["txt"])

job_spec_text = st.text_area("Cut-and-paste your job spec here", 
                             value="Company Name: [fill in]\n[job spec goes here]",
                             height=100)

col3,col4 = st.columns(2)

if col3.button("Cover Letter"):
    if resume and job_spec_text:

        resume_txt = extract_text_from_pdf(resume)
        cover_letter = generate_cover_letter(resume_txt, job_spec_text)
        st.markdown(cover_letter)
        zip_it("job_spec", job_spec_text, resume.getvalue(), cover_letter)
    else:
        st.error("Please upload both a resume and job spec")


if col4.button("Assessment and Questions"):
    if resume and job_spec_text:
        the_resume = extract_text_from_pdf(resume)
        a_and_q = assess_and_questions(the_resume, job_spec_text)
        st.markdown(a_and_q.assessment)
        st.markdown("Here are some questions for the candidate:")
        for question in a_and_q.questions:
            st.markdown('- '+question)
        zip_it("a_and_q", job_spec_text, resume.getvalue(), a_and_q.json(indent=2))
    else:
        st.error("Please upload both a resume and job spec")
