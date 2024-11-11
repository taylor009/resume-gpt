# Resume-GPT

An AI-powered resume optimization tool that analyzes and enhances resumes based on job descriptions.

## Features

- **Job Description Analysis**: Automatically extracts requirements from LinkedIn job postings
- **Resume Analysis**: Evaluates resumes against job requirements providing:
  - Match Score (0-100%)
  - Key Matches
  - Missing Skills/Requirements
  - Suggested Improvements
- **Resume Optimization**: Generates an optimized version of your resume that:
  - Highlights relevant experience and skills
  - Addresses missing requirements where possible
  - Uses strong action verbs
  - Quantifies achievements
  - Maintains professional formatting

## Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-gpt.git
cd resume-gpt
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Usage

1. Run the Streamlit app:
```bash
streamlit run main.py
```

2. Enter a LinkedIn job URL
3. Upload your resume(s) in PDF format
4. Click "Generate Optimal Resume"
5. Review the analysis and optimized resume
6. Download the analysis and/or optimized resume

## Technologies Used

- [Streamlit](https://streamlit.io/) - Web interface
- [LangChain](https://python.langchain.com/) - LLM integration
- [OpenAI GPT-4](https://openai.com/) - AI model
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF processing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- The Streamlit team for their excellent framework
- The LangChain team for their powerful LLM tools
