import streamlit as st
import pdfminer.high_level
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import List
from dotenv import load_dotenv
import os
import tempfile
import requests
from bs4 import BeautifulSoup
import time
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Step 1: Extract Job Requirements
def extract_job_requirements(job_url: str) -> str:
    """Fetch job description from LinkedIn URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Implement exponential backoff
        max_retries = 3
        retry_delay = 5  # Start with 2-second delay
        
        for attempt in range(max_retries):
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            response = requests.get(job_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_description = soup.find('div', {'class': 'description__text'})
                if job_description:
                    return job_description.get_text(strip=True)
                return ""
            elif response.status_code == 429:
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    continue
            else:
                response.raise_for_status()
                
        return "Unable to fetch job description due to rate limiting. Please try again later."
        
    except Exception as e:
        print(f"Error fetching job description: {e}")
        return "Error fetching job description. Please check the URL and try again."

# Step 2: Parse Existing Resumes
def parse_resume(uploaded_file) -> str:
    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file.flush()
        # Extract text from the temporary file
        resume_text = pdfminer.high_level.extract_text(tmp_file.name)
    # Clean up the temporary file
    os.unlink(tmp_file.name)
    return resume_text

# Step 3: Match and Optimize the Resume
def match_resume_to_job(job_requirements: List[str], resume_text: str) -> str:
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name="gpt-4o-mini",
        temperature=0.1,
        verbose=True
    )
    
    prompt = PromptTemplate(
        input_variables=["job_requirements", "resume_text"],
        template="""
        Analyze the following resume against the job requirements and provide specific recommendations:
        
        Job Requirements:
        {job_requirements}
        
        Resume:
        {resume_text}
        
        Please provide:
        1. Match Score (0-100%)
        2. Key Matches
        3. Missing Skills/Requirements
        4. Suggested Improvements
        """
    )
    
    # Create the chain using the new pipe syntax
    chain = prompt | llm | StrOutputParser()
    
    # Create input dictionary
    input_data = {
        "job_requirements": job_requirements,
        "resume_text": resume_text
    }
    
    return chain.invoke(input_data)

def generate_optimized_resume(job_requirements: str, resume_text: str, analysis: str) -> str:
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name="gpt-4-turbo-preview",
        temperature=0.1
    )
    
    prompt = PromptTemplate(
        input_variables=["job_requirements", "resume_text", "analysis"],
        template="""
        Based on the job requirements and analysis, generate an optimized version of the resume.
        
        Job Requirements:
        {job_requirements}
        
        Original Resume:
        {resume_text}
        
        Analysis and Suggestions:
        {analysis}
        
        Please generate an improved version of the resume in markdown format that:
        1. Highlights relevant experience and skills
        2. Addresses missing requirements where possible
        3. Uses strong action verbs
        4. Quantifies achievements
        5. Maintains professional formatting
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({
        "job_requirements": job_requirements,
        "resume_text": resume_text,
        "analysis": analysis
    })

# Streamlit UI
def main():
    st.title("Job Resume Optimizer")

    # Input fields
    job_url = st.text_input("Enter the LinkedIn job URL:")
    uploaded_files = st.file_uploader("Upload your resume(s)", type=["pdf"], accept_multiple_files=True)

    if st.button("Generate Optimal Resume"):
        if job_url:
            with st.spinner("Fetching job description..."):
                job_description = extract_job_requirements(job_url)
                if job_description:
                    st.success("✅ Job description fetched successfully")

                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            with st.spinner(f"Analyzing resume: {uploaded_file.name}"):
                                resume_text = parse_resume(uploaded_file)
                                analysis = match_resume_to_job(job_description, resume_text)

                                # Create an expander for each resume analysis
                                with st.expander(f"Analysis for {uploaded_file.name}", expanded=True):
                                    # Display the analysis in a formatted text area
                                    st.text_area("Analysis Results", value=analysis, height=400, disabled=True)
                                    
                                    # Generate optimized resume - Remove the button and generate automatically
                                    with st.spinner("Generating optimized resume..."):
                                        optimized_resume = generate_optimized_resume(
                                            job_description, 
                                            resume_text, 
                                            analysis
                                        )
                                        st.markdown("### Optimized Resume")
                                        st.markdown(optimized_resume)
                                        
                                        # Add download buttons for both analysis and optimized resume
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.download_button(
                                                label="Download Analysis",
                                                data=str(analysis).encode('utf-8'),
                                                file_name=f"analysis_{uploaded_file.name}.txt",
                                                mime="text/plain"
                                            )
                                        with col2:
                                            st.download_button(
                                                label="Download Optimized Resume",
                                                data=str(optimized_resume).encode('utf-8'),
                                                file_name=f"optimized_{uploaded_file.name}.md",
                                                mime="text/markdown"
                                            )
                    else:
                        st.warning("Please upload at least one resume")
                else:
                    st.error("Could not fetch job description. Please check the URL.")
        else:
            st.warning("Please enter a LinkedIn job URL")

if __name__ == '__main__':
    main()