from chromadb.utils import embedding_functions
from chromadb.config import Settings
import chromadb
import os
from llama_index.core import SimpleDirectoryReader
from chain import Chain
from langchain_groq import ChatGroq
import PyPDF2
import json
from langchain_core.output_parsers import JsonOutputParser

class ResumeSkillExtractor:
    def __init__(self, resume_path="C:/Users/USER/Desktop/python_practice/jobscan_App/resources/resume.pdf"):
        self.resume_path = resume_path
        self.chroma_client = chromadb.Client(Settings())
        self.embedding_function = self.custom_embedding_function()
        self.collection=self.chroma_client.get_or_create_collection(name="resume_skills")
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-70b-versatile",
        )
        
    def custom_embedding_function(self):
        llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-70b-versatile",
        )
            
    def extract_pdf_text(self,pdf_file):
        text = ""
        try:
            #with open(pdf_text, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    def extract_summary_and_skills(self, text):
        prompt = f"""
        Your task is to extract all relevant information mentioned only in the *PROFESSIONAL SUMMARY* and *SKILLS* sections, including:
         - Both **technical and non-technical skills** mentioned in the text.
         - **Fields of study**, academic disciplines, or areas of expertise.
         - Include everything as a unified list.

        ### INSTRUCTIONS:
        1. Normalize all skills and areas of study to a consistent format (e.g., lowercase, no additional descriptions).
        2. Provide the output in JSON format with the key `"skills"` as a list.

         ### VALID JSON (NO PREAMBLE):

        Text:
        {text}
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Error extracting content with LLM: {e}")
            return None
        
    def store_resume_skills(self,uploaded_file):
        """
        Parse the resume PDF, extract the text, and store the skills into ChromaDB.
        """
        try:
            # Extract text from the resume PDF
            print("Extracting text from the resume file...")
            resume_text = self.extract_pdf_text(uploaded_file)
            if not resume_text:
                raise ValueError("No text extracted from the resume PDF.")
            
            print("Extracting Professional Summary and Skills using LLM...")
            extracted_content = self.extract_summary_and_skills(resume_text)

            if not extracted_content:
                raise ValueError("Failed to extract content using LLM.")
            print("Extracted Content:", extracted_content)
            
            print("Collection initialized in ChromaDB.")
            
            cleaned_content = extracted_content.strip("```json").strip("```").strip()
            print("Cleaned LLM Response:", cleaned_content)
            #json_parser = JsonOutputParser()
            #json_res = json_parser.parse(cleaned_content)
            
            
            try:
               extracted_data = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
              raise ValueError(f"Failed to parse LLM response as JSON. Error: {e}")
            skills = extracted_data.get("skills", [])
            return extracted_data if isinstance(extracted_data, list) else [extracted_data]
            #soft_skills = extracted_data.get("soft_skills", [])

            # Add the resume content to the ChromaDB collection
            self.collection.add(
                documents=[resume_text],
                metadatas=[{"source": "resume.pdf"}],
                ids=["resume_1"]
            )
            print("Resume skills stored successfully in ChromaDB.")
            
             # Store hard skills and soft skills in the vector database
            for idx, skill in enumerate(skills):
                self.collection.add(
                    documents=[skill],
                    metadatas=[{"type": "skill", "source": "resume.pdf"}],
                    ids=[f"skill_{idx}"]
                )
                
            print("Hard and soft skills stored successfully in ChromaDB.")
            return json_res
        except Exception as e:
            print(f"An error occurred: {e}")

    #def query_links(self, skills):
        # return self.query_stored_skills(query_text="skill")
        
# Usage
if __name__ == "__main__":
    # Provide the path to the resume
    resume_path = r"C:/Users/USER/Desktop/python_practice/jobscan_App/resources/resume.pdf"
    # Initialize the class and call the function
    #resume_parser = ResumeSkillExtractor(resume_path=resume_path)
    #resume_parser.store_resume_skills()
