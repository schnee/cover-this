import streamlit as st
from interviews.jobfit import run_interview
from pdf_utils import extract_text_from_pdf


jobspec = st.text_area("Please enter the job description here (If you don't have one, enter keywords, such as PostgreSQL or Python instead): ")
resume = st.file_uploader("Please upload your resume here (PDF format): ")
assessment = st.text_area("Please enter your resume assessment here: ")
init_questions = st.text_area("Please enter your initial questions here: ")
    

if(jobspec and resume):
    resume_str = extract_text_from_pdf(resume)

    run_interview(jobspec, resume_str, assessment, init_questions)