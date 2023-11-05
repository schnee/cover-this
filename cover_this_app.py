import streamlit as st
from cover_chain import generate_cover_letter
from io import StringIO
from io_utils import zip_it
from mocker import assess_and_questions

from pdf_utils import extract_text_from_pdf
from models import QuestionList

# this is the main app

st.title("Mahkr Cover Letter Generator")



st.markdown("""Stuck on writing a cover letter? Need some prep for an interview? Then this 
            app is for you. Upload a resume, provide a job spec, and let AI do its thing. You can
            get either a DRAFT cover letter or a job-assesment and list of sample questions at the 
            push of a button.
            
            This site collects session-level information to improve the quality of the service provided.""")

st.markdown("""If you like this app, please consider buying me a coffee. :coffee: :coffee: :coffee:
            """)

col1, col2 = st.columns(2)

col1.link_button(":orange[:coffee: Buy me a coffee :coffee:]", "https://www.buymeacoffee.com/mahkr",)
#st.markdown("[![Buy me a coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/mahkr)")
col2.link_button("Email me with feedback :email:", "mailto:schneeman@gmail.com?subject=Mahkr Feedback")

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
        zip_it("c_l", job_spec_text, resume.getvalue(), cover_letter)
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
