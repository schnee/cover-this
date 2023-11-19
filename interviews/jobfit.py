import streamlit as st
from typing import Literal
from dataclasses import dataclass
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain, RetrievalQA
from langchain.prompts.prompt import PromptTemplate
from langchain.text_splitter import NLTKTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import nltk
from io_utils import zip_eval
from llmfactory import LLMFactory
from prompts.prompts import templates


@dataclass
class Message:
    """class for keeping track of interview history."""
    origin: Literal["human", "ai"]
    message: str

    def __str__(self) -> str:
        return f"{self.origin}: {self.message}"

def save_vector(text):
    """embeddings"""

    text_splitter = NLTKTextSplitter()
    texts = text_splitter.split_text(text)
     # Create emebeddings
    embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["llm_configuration"]["OPENAI_API_KEY"])
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch

def initialize_session_state_interview(jd, assessment, init_questions):
    
    # initialize the LLM Factory
    factory = LLMFactory()

    # Ensure we have the tokenizer
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError: 
        print('Downloading punkt')
        nltk.download('punkt')

    # initialize session states
    if 'jd_docsearch' not in st.session_state:
        st.session_state.jd_docsearch = save_vector(jd)
    if 'assessment' not in st.session_state:
        st.session_state.assessment = assessment
    if 'init_questions' not in st.session_state:
        st.session_state.init_questions = init_questions
    if 'jd_retriever' not in st.session_state:
        st.session_state.jd_retriever = st.session_state.jd_docsearch.as_retriever(search_type="similarity")
    if 'jd_chain_type_kwargs' not in st.session_state:
        pv = {"assessment": st.session_state.assessment}
        Interview_Prompt = PromptTemplate(input_variables=["context", "question"],
                                          partial_variables=pv,
                                          template=templates.jd_template)
        st.session_state.jd_chain_type_kwargs = {"prompt": Interview_Prompt}
    if 'jd_memory' not in st.session_state:
        st.session_state.jd_memory = ConversationBufferMemory()
    # interview history
    if "jd_history" not in st.session_state:
        st.session_state.jd_history = []
        st.session_state.jd_history.append(Message("ai",
                                                   "Hello, Welcome to the interview. I am Mahkr, your interviewer for today. We are here to determine your fit for the job in the specification."
                                                   "Please start by introducing a little bit about yourself. Your answers can be a few paragraphs long if needed."))
    # token count
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    # cost
    if "interview_cost" not in st.session_state:
        st.session_state.interview_cost = 0
    if "jd_guideline" not in st.session_state:
        llm = factory.create_generator()
        st.session_state.jd_guideline = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type_kwargs=st.session_state.jd_chain_type_kwargs, chain_type='stuff',
            retriever=st.session_state.jd_retriever, 
            memory = st.session_state.jd_memory).run("""Create an interview guideline and prepare only one question for each topic in the job description. 
                                                     Make sure the prepared questions test the candidate's knowledge of the job description's topics.""")
    # llm chain and memory
    if "jd_screen" not in st.session_state:
        llm = factory.create_generator()
        PROMPT = PromptTemplate(
            input_variables=["history", "input"],
            template=templates.jd_screen_template)

        st.session_state.jd_screen = ConversationChain(prompt=PROMPT, llm=llm,
                                                           memory=st.session_state.jd_memory)
    if 'jd_feedback' not in st.session_state:
        llm = factory.create_generator()
        st.session_state.jd_feedback = ConversationChain(
            prompt=PromptTemplate(input_variables=["history", "input"], template=templates.feedback_template),
            llm=llm,
            memory=st.session_state.jd_memory,
            return_final_only=True
        )

def answer_call_back():
    with get_openai_callback() as cb:
        # user input
        human_answer = st.session_state.answer
        input = human_answer

        st.session_state.jd_history.append(
            Message("human", input)
        )
        # OpenAI answer and save to history
        llm_answer = st.session_state.jd_screen.run(input = human_answer)
  
        st.session_state.jd_history.append(
            Message("ai", llm_answer)
        )
        st.session_state.token_count += cb.total_tokens
        st.session_state.interview_cost += cb.total_cost
        return 
    
def run_interview(jobspec, resume, assessment, init_questions):
    if jobspec and assessment and init_questions:
        # initialize session states
        initialize_session_state_interview(jobspec, assessment, init_questions)
        #st.write(st.session_state.jd_guideline)
        interview_progress = st.empty()
        col1, col2 = st.columns(2)
        with col1:
            feedback = st.button("Interview Feedback")
        with col2:
            guideline = st.button("Interview Guideline")
        chat_placeholder = st.container()
        answer_placeholder = st.container()
        
        if guideline:
            st.write(st.session_state.jd_guideline)
        if feedback:
            evaluation = st.session_state.jd_feedback.run("""please give evaluation regarding the interview. 
                                                          take it one step at a time and keep the evaluation to less than 2500 words.
                                                          this evaluation is very important to securing the role.""")
            st.markdown(evaluation)
            # create the strings to zip up
            the_interview = ""
            for message in st.session_state.jd_history:
                the_interview += message.origin + ": " + message.message + "\n\n"
                
            zip_eval(the_interview, evaluation, st.session_state.jd_guideline)
            st.download_button(label="Download Interview Feedback", data=evaluation, file_name="interview_feedback.txt")
            st.stop()
        else:
            with answer_placeholder:
                answer = st.chat_input("Your answer")
                if answer:
                    st.session_state['answer'] = answer
                    answer_call_back()
            interaction_len = 0# len(st.session_state.jd_history)
            with chat_placeholder:
                # suppress system messages

                for answer in st.session_state.jd_history:
                    if answer.origin == 'ai':
                        with st.chat_message("assistant"):
                            st.write(answer.message)
                        interaction_len += 1#len(answer.message)
                    elif answer.origin == 'human':
                        with st.chat_message("user"):
                            st.write(answer.message)
                        interaction_len += 1# len(answer.message)

            
            cost_in_pennies = 100*round(st.session_state.interview_cost, 3)
            interview_progress.caption(f"""
            Progress: {100*round(interaction_len / 30, 2)}% completed.\n
            Effort: {cost_in_pennies}""")
    else:
        st.info("Please submit a job description, resume, and initial assessment to start the interview.")
