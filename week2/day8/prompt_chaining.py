import os
from dotenv import load_dotenv
from groq import Groq
from time import sleep

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API Error")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"

JD="""
Role Overview We are looking for a skilled and motivated Frontend Developer with 3 to 8 years of experience in designing and developing modern enterprise applications. 
The ideal candidate should have strong handson expertise in Angular 19 and above for frontend development.
This role requires experience in building scalable, secure, and high-performance full stack applications, 
 with exposure to cloud-native development, containerized deployment models, and CI/CD-based automated deployments.
The candidate should be comfortable working across frontend APIs, databases, and deployment pipelines in an Agile development environment.
 Key Responsibilities • Design, develop, test, and maintain frontend applications using Angular 19+. • Build responsive, reusable, and high-performance user interfaces using
 Angular, TypeScript, HTML5, CSS3, and related frontend technologies. • Design and implement microservices-based architecture
 for scalable and modular application development. • Ensure application security, code quality, performance, scalability, and maintainability by 
 following engineering best practices. • Participate in code reviews, troubleshooting, debugging, and performance
   optimization across frontend and backend layers. • Prepare and maintain technical documentation for application features, 
   APIs, deployment steps, and architecture decisions. • Participate in code reviews, troubleshooting, debugging, and performance optimization across frontend and backend layers.
 • Prepare and maintain technical documentation for application features, APIs, deployment steps, and architecture decisions. 

Required Skills Frontend • Strong experience in Angular 19 and above 
• Proficiency in TypeScript, JavaScript, HTML5, CSS3 • Experience in building responsive and component-based web applications Architecture & Database 
• Experience with microservices architecture • Good knowledge of relational databases such as Oracle, MySQL and PostgreSQL DevOps / Cloud / Deployment 
• Exposure to cloud-native development • Experience with Docker and preferably Kubernetes 
• Familiarity with Git and version control workflows Preferred Qualifications 
• Bachelor’s degree in Computer Science /Information Technology, or B.Sc. – IT, MCA 
"""

reusme="""
Priyanka Vishwakarma
Mumbai, Maharashtra, India | vishwakarmapriyanka84@gmail.com | linkedin.com/in/priyankavishwakarma |
9764358712
Professional Summary
Full Stack Developer with 3.5+ years of experience building scalable web applications using the MEAN stack (MySQL,
Express.js, Angular, Node.js). Proven track record in the EduTech and FinTech domains, delivering real-time systems,
REST API integrations, and RBAC-based access control. Adept at both frontend and backend development, with a strong
focus on performance optimization and clean architecture. Currently open to Backend or Full Stack Developer roles.
Technical Skills
Languages & Frameworks: JavaScript, TypeScript, Node.js, Angular 19, Express.js, React
Databases: MySQL, MongoDB
Tools & Platforms: REST APIs, Rabbitmq, Keycloak (SSO/RBAC), Docker (basic), Git, Postman, Linux (basic),
CI/CD Pipeline, AWS
Concepts: Full Stack Development, SaaS Architecture, Role-Based Access Control (RBAC), MVC Architecture,
Microservices, Authentication(JWT), API Security, Performance Optimization, Agile/Scrum, Problem Solving
Certifications: Angular (HackerRank), Java (HackerRank), SQL (HackerRank), HTML
Experience
Trace – AI-Powered Fraud Detection & Background Verification Nov 2025 – Jun 2026
Frontend Developer Mumbai, India (Remote)
– Developed and maintained Angular-based frontend modules for an AI-powered fraud detection and background
verification platform.
– Collaborated with backend teams to integrate REST APIs, ensuring accurate real-time rendering of verification
results.
– Participated in code reviews and contributed to improving frontend build pipelines and component reusability.
Edulab Educational Exchange Pvt. Ltd. Jun 2022 – Jul 2025
Software Developer (Full Stack) Andheri, Mumbai
– Built and maintained full-stack features for an EduTech SaaS platform serving thousands of users, using Angular
(frontend) and Node.js/Express.js (backend).
– Designed and integrated RESTful APIs for core modules including user management, course delivery, and real-time
assessments.
– Implemented Role-Based Access Control (RBAC) using Keycloak, enabling secure multi-tenant access management
across student, instructor, and admin roles.
– Optimized MySQL and MongoDB queries, reducing average API response times and improving overall platform
performance.
– Collaborated with cross-functional teams (design, QA, product) to deliver new features on schedule in an agile
environment.
– Containerized development environments using Docker and managed source control and CI workflows using Git.
– Progressed from Junior Software Developer (Jun–Sep 2022) to Software Developer within 4 months based on
performance.
Projects
HSNC Admission Desk | Node.js, HTML/CSS, JavaScript, Angular 17, MySQL
– Designed and deployed an automated process showcasing projects skills and experience.
Personal Portfolio Website | Node.js, HTML/CSS, JavaScript, React
– Designed and deployed a personal portfolio at priyankavishwakarma.onrender.com showcasing projects, skills, and
experience, hosted on Render.
Education
Annasaheb Vartak College of Arts, Commerce & Science 2017 – 2021
Bachelor of Science in Information Technology (B.Sc. IT) Mumbai, India
"""

def ask_llm(system_prompt,user_prompt):
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response=client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def step1_resume_extractor():
    system_prompt="""
    You are a professional HR assistant. You have to extract the skiills from the resume provided by the user.
    Only return the extracted skills no other infromation. Do not invent any skills from your self.
    """

    user_prompt=f"""
    Here is the resume of a candidate:
    {reusme}
    """
    return ask_llm(system_prompt,user_prompt)

def step2_JD_extractor():
    system_prompt="""
    You are a professional HR assistant. You have to extract the skiills from the Job Description provided by the user.
    Only return the extracted skills no other infromation. Do not invent any skills from your self.
    """

    user_prompt=f"""
    Here is the Job Description:
    {JD}
    """
    return ask_llm(system_prompt,user_prompt)

def step3_match_skills(candidate_skills,job_skills):
    system_prompt="""
    You are a professional HR assistant. You have to compare the candidate skills and the Job Description skills and based on that
    return the score between 1 to 100 also provide a short feedback on the candidate skills and the Job Description skills.
    Only return the score and the feedback no other infromation. Do not invent any skills from your self. The score should be based on the number of skills matched between the candidate and the Job Description. The feedback should be a short paragraph on the candidate skills and the Job Description skills. 
    """

    user_prompt=f"""
    Here are the skills of the candidate:
    {candidate_skills}
    
    Here are the skills required in the Job Description:
    {job_skills}
    """
    return ask_llm(system_prompt,user_prompt)

candidate_skills=step1_resume_extractor()
sleep(2)
job_skills=step2_JD_extractor()
sleep(2)
score_feedback=step3_match_skills(candidate_skills,job_skills)
print("Candidate Skills:",candidate_skills)
print("Job Description Skills:",job_skills)
print("Score and Feedback:",score_feedback)

    