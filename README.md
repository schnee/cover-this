![flow of action from spec and resume to cover letter](img/cover-flow.png)

# Cover This
Assists in creating job application cover letters via LLM (ChatGPT) summaries
and generative AI. Langchain is used to navigate the OpenAI APIs.

```
├── cover-chain.py
├── cover-letter.txt
├── cover-this.py
├── img
│   └── cover-flow.png
├── job-spec.txt
├── README.md
└── schneeman-brent-resume.pdf
```

The main executable is `cover-chain.py` and is invoked via `/bin/python3 /home/brent/projects/tworavens/github/cover-this/cover-chain.py`.
It reads the `job-spec.txt` file, summarizes it, reads the `schneeman-brent-resume.pdf` file and builds a 
prompt with the summarized spec and the resume which asks the LLM to write a cover letter. 

The cover is output to console, and written to the `cover-letter.txt` file.

The `job-spec.txt` is copy-pasted text from whatever website lists the spec. This seems more direct than
programmatically reading the website directly as certain job boards require authentication for access
and I didn't want to bite off OAUTH (e.g.) in this simple program.

The generated cover letter requires proofing and editing. It is generally good English, but the LLM
can (and does) hallucinate experience. For example, I apparently have multiple concurrent PhDs
(which I do not). The generated cover is a good start.