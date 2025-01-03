import os
import streamlit as st
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from io import StringIO
import glob
import PyPDF2

# Load environment variables
load_dotenv()

# Function to read the file with flexible encoding handling
def read_file_with_fallback(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        # Fallback to ISO-8859-1 or latin-1
        try:
            return uploaded_file.read().decode("ISO-8859-1")
        except UnicodeDecodeError:
            st.error(f"Error decoding file {uploaded_file.name}. Unsupported encoding.")
            return None

# Function to extract text from PDF files
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to process the uploaded resumes and job description
def process_resumes_and_description(job_description, resumes):
    # Create Candidate Screening Agent using uploaded job description
    candidate_screener = Agent(
        role="Senior Talent Acquisition Specialist",
        goal="Identify the top 3 candidates who best match the job description for a Senior Product Manager in AI Chat Assistant development",
        backstory="""You are an experienced talent acquisition specialist with deep expertise in tech recruiting, 
        particularly in AI and product management roles. Your keen eye for detail allows you to match candidate 
        backgrounds precisely to job requirements.""",
        verbose=True,
        llm="gpt-4o-mini"
    )

    # Create Screening Task
    screening_task = Task(
        description=f"""Carefully review the job description and each candidate's resume:
        1. Analyze how each candidate's experience aligns with the job requirements
        2. Pay special attention to:
           - Experience in AI/ML product management
           - Technical understanding of complex software products
           - Track record of successful product launches
        3. Rank the candidates and provide a detailed rationale for the top 3 selections
        4. Explain why these candidates stand out for this specific AI Chat Assistant Product Manager role

        Job Description:
        {job_description}

        Candidate Resumes:
        {', '.join([f"{candidate['name']}: {candidate['resume']}" for candidate in resumes])}
        """,
        expected_output="",
        agent=candidate_screener
    )

    # Instantiate the Crew
    crew = Crew(
        agents=[candidate_screener],
        tasks=[screening_task],
        verbose=False,
    )

    # Kickoff the task and get the result
    result = crew.kickoff()
    return result

# Streamlit UI setup
st.title("Resume Screening")
st.subheader("Upload your job description and candidate resumes for screening.")

# Job Description input (Upload file or paste text)
jd_option = st.radio("Select the Job Description Input Method", ("Upload Job Description File", "Paste Job Description Text"))

if jd_option == "Upload Job Description File":
    uploaded_jd = st.file_uploader("Upload Job Description (Text File)", type=["txt"])
    
    if uploaded_jd:
        job_description = uploaded_jd.read().decode("utf-8")
        st.text_area("Job Description", value=job_description, height=200, disabled=True)
    else:
        job_description = ""
        
elif jd_option == "Paste Job Description Text":
    job_description = st.text_area("Paste the Job Description", height=300)

# Resume upload section
uploaded_files = st.file_uploader("Upload Resumes (PDF or Text Files)", type=["pdf", "txt"], accept_multiple_files=True)

# Option to upload a folder of resumes (if applicable)
uploaded_folder = st.text_input("Alternatively, enter the folder path for resumes (if on local machine)")

# Process resumes and job description
if uploaded_files:
    resumes = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        
        # Handle PDF files differently
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = read_file_with_fallback(uploaded_file)

        # Proceed if decoding was successful
        if resume_text:
            # Add the resume and its name to the resumes list
            resumes.append({"name": file_name, "resume": resume_text})

    if job_description:
        # Process the resumes and job description
        st.write("Processing the resumes and job description...")
        result = process_resumes_and_description(job_description, resumes)
        st.write("### Top 3 Candidates:")
        st.write(result)
    else:
        st.warning("Please upload or paste a job description.")
        
elif uploaded_folder:
    # If folder path is provided (for local directories)
    resumes = []
    resume_files = glob.glob(os.path.join(uploaded_folder, "*.txt"))  # Assuming resumes are in .txt format

    for resume_file in resume_files:
        with open(resume_file, "r") as file:
            resume_text = file.read()

        # Extract resume name from file path
        file_name = os.path.basename(resume_file)
        resumes.append({"name": file_name, "resume": resume_text})

    if job_description:
        # Process the resumes and job description
        st.write("Processing the resumes and job description...")
        result = process_resumes_and_description(job_description, resumes)
        st.write("### Top 3 Candidates:")
        st.write(result)
    else:
        st.warning("Please upload or paste a job description.")
        
else:
    st.info("Please upload resumes or provide a folder path.")




# import os
# import streamlit as st
# from crewai import Agent, Task, Crew
# from dotenv import load_dotenv
# from io import StringIO
# import glob

# # Load environment variables
# load_dotenv()

# # Function to process the uploaded resumes and job description
# def process_resumes_and_description(job_description, resumes):
#     # Create Candidate Screening Agent using uploaded job description
#     candidate_screener = Agent(
#         role="Senior Talent Acquisition Specialist",
#         goal="Identify the top 3 candidates who best match the job description for a Senior Product Manager in AI Chat Assistant development",
#         backstory="""You are an experienced talent acquisition specialist with deep expertise in tech recruiting, 
#         particularly in AI and product management roles. Your keen eye for detail allows you to match candidate 
#         backgrounds precisely to job requirements.""",
#         verbose=True,
#         llm="gpt-4"
#     )

#     # Create Screening Task
#     screening_task = Task(
#         description=f"""Carefully review the job description and each candidate's resume:
#         1. Analyze how each candidate's experience aligns with the job requirements
#         2. Pay special attention to:
#            - Experience in AI/ML product management
#            - Technical understanding of complex software products
#            - Track record of successful product launches
#         3. Rank the candidates and provide a detailed rationale for the top 3 selections
#         4. Explain why these candidates stand out for this specific AI Chat Assistant Product Manager role

#         Job Description:
#         {job_description}

#         Candidate Resumes:
#         {', '.join([f"{candidate['name']}: {candidate['resume']}" for candidate in resumes])}
#         """,
#         expected_output="",
#         agent=candidate_screener
#     )

#     # Instantiate the Crew
#     crew = Crew(
#         agents=[candidate_screener],
#         tasks=[screening_task],
#         verbose=False,
#     )

#     # Kickoff the task and get the result
#     result = crew.kickoff()
#     return result

# # Streamlit UI setup
# st.title("AI Chat Assistant Product Manager - Resume Screening")
# st.subheader("Upload your job description and candidate resumes for screening.")

# # Job Description input (Upload file or paste text)
# jd_option = st.radio("Select the Job Description Input Method", ("Upload Job Description File", "Paste Job Description Text"))

# if jd_option == "Upload Job Description File":
#     uploaded_jd = st.file_uploader("Upload Job Description (Text File)", type=["txt"])
    
#     if uploaded_jd:
#         job_description = uploaded_jd.read().decode("utf-8")
#         st.text_area("Job Description", value=job_description, height=200, disabled=True)
#     else:
#         job_description = ""
        
# elif jd_option == "Paste Job Description Text":
#     job_description = st.text_area("Paste the Job Description", height=300)

# # Resume upload section
# uploaded_files = st.file_uploader("Upload Resumes (PDF or Text Files)", type=["pdf", "txt"], accept_multiple_files=True)

# # Option to upload a folder of resumes (if applicable)
# uploaded_folder = st.text_input("Alternatively, enter the folder path for resumes (if on local machine)")

# # Process resumes and job description
# if uploaded_files:
#     resumes = []
#     for uploaded_file in uploaded_files:
#         file_name = uploaded_file.name
#         resume_text = uploaded_file.read().decode("utf-8")

#         # Add the resume and its name to the resumes list
#         resumes.append({"name": file_name, "resume": resume_text})

#     if job_description:
#         # Process the resumes and job description
#         st.write("Processing the resumes and job description...")
#         result = process_resumes_and_description(job_description, resumes)
#         st.write("### Top 3 Candidates:")
#         st.write(result)
#     else:
#         st.warning("Please upload or paste a job description.")
        
# elif uploaded_folder:
#     # If folder path is provided (for local directories)
#     resumes = []
#     resume_files = glob.glob(os.path.join(uploaded_folder, "*.txt"))  # Assuming resumes are in .txt format

#     for resume_file in resume_files:
#         with open(resume_file, "r") as file:
#             resume_text = file.read()

#         # Extract resume name from file path
#         file_name = os.path.basename(resume_file)
#         resumes.append({"name": file_name, "resume": resume_text})

#     if job_description:
#         # Process the resumes and job description
#         st.write("Processing the resumes and job description...")
#         result = process_resumes_and_description(job_description, resumes)
#         st.write("### Top 3 Candidates:")
#         st.write(result)
#     else:
#         st.warning("Please upload or paste a job description.")
        
# else:
#     st.info("Please upload resumes or provide a folder path.")
