import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-70b-versatile",
        )
    def extract_jobs(self, pagedata):
        prompt_extract = PromptTemplate.from_template(
            """
            ### Job description:
            {page_data}
    
            ### INSTRUCTION:
          Your task is to:

         1. Identify and extract all the skills mentioned in the provided text, including both technical skills (e.g., programming languages, tools, domain-specific expertise) and non-technical skills (e.g., communication, problem-solving).
         2. Ignore locations, or any other irrelevant details.
         3. Provide the output in JSON format under a single key called "skills" as a list.
    
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": pagedata})

        try:
            json_parser = JsonOutputParser()
            json_res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return json_res if isinstance(json_res, list) else [json_res]
    
    def find_missing_skills(self, job_skills, resume_skills):
    #    job_skills = set(job_skills[0].get("skills", []) if isinstance(job_skills, list) and job_skills else [])
    #    resume_skills = set(resume_skills[0].get("skills", []) if isinstance(resume_skills, list) and resume_skills else [])
       
       # Extract and lowercase skills for case-insensitive comparison
       job_skills = set(skill.lower().strip() for skill in job_skills[0].get("skills", []) if isinstance(job_skills, list) and job_skills)
       resume_skills = set(skill.lower().strip() for skill in resume_skills[0].get("skills", []) if isinstance(resume_skills, list) and resume_skills)

       missing_skills = [x for x in job_skills if x not in resume_skills] #job_skills - resume_skills
       return list(missing_skills)
    
    def find_ATS_score(self, job_skills, resume_skills):
        # prompt = f"""
        # ###Parameters:
        # {job_skills} (list of str): List of skills or keywords from the job description.
        # {resume_skills} (list of str): List of skills or keywords from the resume.
        
        # Calculate ATS score based on exact matching between job skills and resume skills and give the value in percentage.
        
        # Returns:VALID float (NO PREAMBLE):
        # Only return the ATS score as a percentage of matching skills.
        
        # """
        # res = self.llm.invoke(prompt)
        # print(res.content.strip())
        # try:
        #    # Ensure only the numeric value is returned
        #     ats_score = float(res.content.strip())
        # except ValueError:
        #   raise ValueError(f"Unexpected response format: {res.content}")
    
        # return ats_score
    
        # Convert all skills to lowercase for case-insensitive matching
        # job_skills = set(job_skills[0].get("skills", []) if isinstance(job_skills, list) and job_skills else [])
        # resume_skills = set(resume_skills[0].get("skills", []) if isinstance(resume_skills, list) and resume_skills else [])
        
        job_skills = set(skill.lower().strip() for skill in job_skills[0].get("skills", []) if isinstance(job_skills, list) and job_skills)
        resume_skills = set(skill.lower().strip() for skill in resume_skills[0].get("skills", []) if isinstance(resume_skills, list) and resume_skills)

        print(job_skills)
        print(resume_skills)
        # job_skills = [skill.lower().strip() for skill in job_skills]
        # resume_skills = [skill.lower().strip() for skill in resume_skills]
        # Count matches
        matches = sum(1 for skill in job_skills if skill in resume_skills)
        print(matches)
        # Calculate percentage
        ats_score = (matches / len(job_skills)) * 100 if job_skills else 0
        print(ats_score)
        return round(ats_score, 2)
    
    def generate_sentences(self, skill):
        prompt_extract = PromptTemplate.from_template(
            """
            ### Job description:
            Skill: {skill}
    
            ### INSTRUCTION:
          Your task is to generate 3 valid and professional sentences that describe the experience or proficiency with the given skill. 

          Instructions:
          1. Ensure the sentences are relevant for a professional resume.
          2. Each sentence should highlight different aspects, such as:
            - Experience using the skill in a project or job.
            - Proficiency or expertise in the skill.
            - The impact of the skill on work or outcomes.
          3. Use action verbs and concise language.

           Output:    
            ### Provide 3 sentences in a bulleted format. Do not include preambles or explanations.
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"skill": skill})
        return res.content
        

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
    chain=Chain()
    #chain.extract_jobs("Student in computer science or equivalent degree")
    
