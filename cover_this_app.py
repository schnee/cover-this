import streamlit as st
from cover_chain import generate_cover_letter
from io import StringIO

st.title("Cover Letter Generator")

st.markdown("This app will generate a cover letter based on a PDF resume and a job spec in a text file. Simply upload both and press the 'Generate' button.")
st.link_button(":orange[Buy me a coffee]", "https://www.buymeacoffee.com/mahkr",)
#st.markdown("[![Buy me a coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/mahkr)")
st.link_button("Email me with questions", "mailto:schneeman@gmail.com")
st.header("Upload Resume")
resume = st.file_uploader("Choose a resume", type=["pdf"])

st.header("Upload Job Spec")  
job_spec = st.file_uploader("Choose a job spec", type=["txt"])

if st.button("Generate Cover Letter"):
    if resume and job_spec:
        # To convert to a string based IO:
        stringio = StringIO(job_spec.getvalue().decode("utf-8"))

        # To read file as string:
        job_spec_text = stringio.read()
        cover_letter = generate_cover_letter(resume, job_spec_text)
        st.text(cover_letter)
    else:
        st.error("Please upload both a resume and job spec")



