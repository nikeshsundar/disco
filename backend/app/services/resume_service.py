import re
from typing import List, Dict, Any
import os

# Try to import PDF libraries (may not be available on serverless)
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

# Common skills database for matching
TECH_SKILLS = [
    # Programming Languages
    "python", "javascript", "java", "c++", "c#", "ruby", "go", "rust", "typescript",
    "r", "scala", "kotlin", "swift", "php", "perl", "matlab",
    
    # Web Frameworks
    "react", "reactjs", "react.js", "react native", "angular", "angularjs", "angular.js",
    "vue", "vue.js", "vuejs", "node.js", "nodejs", "node",
    "express", "expressjs", "express.js", "django", "flask", "fastapi",
    "spring", "spring boot", ".net", "asp.net", "laravel", "rails", "next.js", "nextjs",
    "jquery", "backbone", "ember",
    
    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch", "cassandra",
    "oracle", "sqlite", "dynamodb", "firebase", "supabase", "mariadb",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "jenkins", "ci/cd", "circleci", "travis", "terraform", "ansible", "cloudformation",
    "heroku", "vercel", "netlify", "tomcat", "nginx", "apache",
    
    # Build Tools
    "maven", "gradle", "grunt", "gulp", "npm", "yarn", "pnpm",
    
    # Tools & Version Control
    "git", "github", "gitlab", "bitbucket", "linux", "bash", "powershell", "unix",
    "rest api", "rest", "graphql", "microservices", "api integration", "soap",
    
    # AI/ML & Data Science
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "data analysis", "pandas", "numpy", "data science", "nlp", "computer vision",
    "rag", "langchain", "langgraph", "llm", "large language model", "gpt", "openai",
    "hugging face", "transformers", "vector database", "embeddings", "prompt engineering",
    "generative ai", "ai agents", "agentic ai",
    
    # Automation & Testing
    "selenium", "playwright", "puppeteer", "cypress", "pytest", "junit", "mocha", "jest",
    "web scraping", "beautifulsoup", "scrapy", "automation", "exponentjs",
    
    # Data & BI Tools
    "power bi", "tableau", "excel", "looker", "metabase", "superset",
    "apache spark", "hadoop", "airflow", "kafka", "etl",
    
    # Low-code/No-code & Integration
    "n8n", "zapier", "make", "integromat", "retool", "appsmith",
    
    # Frontend
    "html", "css", "sass", "scss", "less", "tailwind", "tailwindcss", "bootstrap", "webpack", "vite",
    "figma", "ui/ux", "responsive design",
    
    # Project Management & Agile
    "agile", "scrum", "jira", "confluence", "trello", "asana", "notion"
]

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "analytical",
    "time management", "project management", "mentoring", "collaboration",
    "adaptability", "creativity", "critical thinking", "decision making",
    "presentation", "negotiation", "stakeholder management"
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e", "bsc", "msc",
    "b.s.", "m.s.", "b.s.b.a", "b.a.", "m.a.", "b.sc", "m.sc",
    "mba", "bca", "mca", "diploma", "certification", "degree", "university", "college",
    "computer science", "information technology", "engineering", "mathematics",
    "digital transformation", "data science", "artificial intelligence",
    "business administration", "management", "information systems"
]

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file using multiple methods"""
    text = ""
    
    # Method 1: Try pdfplumber first
    if HAS_PDFPLUMBER:
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                print(f"pdfplumber extracted {len(text)} chars")
                return text
        except Exception as e:
            print(f"pdfplumber error: {e}")
    
    # Method 2: Try PyMuPDF (fitz)
    if HAS_FITZ:
        try:
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()
            if text.strip():
                print(f"PyMuPDF extracted {len(text)} chars")
                return text
        except Exception as e:
            print(f"PyMuPDF error: {e}")
    
    # Method 3: Try PyPDF2
    if HAS_PYPDF2:
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                print(f"PyPDF2 extracted {len(text)} chars")
                return text
        except Exception as e:
            print(f"PyPDF2 error: {e}")
    
    # If no PDF library available, return error message
    if not HAS_PDFPLUMBER and not HAS_FITZ and not HAS_PYPDF2:
        print("WARNING: No PDF library available")
        return "PDF_LIBRARY_NOT_AVAILABLE"
    
    print(f"WARNING: Could not extract text from PDF. It may be image-based.")
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from Word document"""
    text = ""
    if not HAS_DOCX:
        print("WARNING: python-docx not available")
        return ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
    return text

def extract_email(text: str) -> str:
    """Extract email from text"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else ""

def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    matches = re.findall(phone_pattern, text)
    # Filter out very short matches
    valid_phones = [p for p in matches if len(re.sub(r'\D', '', p)) >= 10]
    return valid_phones[0] if valid_phones else ""

def extract_name(text: str) -> str:
    """Extract candidate name from resume (usually first line or prominent text)"""
    lines = text.strip().split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        # Skip empty lines and lines that look like headers/contact info
        if not line or '@' in line or any(c.isdigit() for c in line[:5]):
            continue
        # Name is usually all caps or title case, 2-4 words
        words = line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return line
    return ""

def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text"""
    text_lower = text.lower()
    found_skills = []
    
    # Skip false positives
    skip_words = ['& certificates', 'technical skills:', 'skills:', 'selenium)']
    
    for skill in TECH_SKILLS + SOFT_SKILLS:
        # Check for whole word match (with word boundaries)
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            skill_title = skill.title()
            # Clean up skill names
            if skill_title.lower() not in skip_words and len(skill_title) > 1:
                found_skills.append(skill_title)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for s in found_skills:
        s_lower = s.lower()
        if s_lower not in seen:
            seen.add(s_lower)
            unique_skills.append(s)
    
    return unique_skills


def extract_experience_years(text: str) -> float:
    """Estimate years of experience from resume"""
    text_lower = text.lower()
    
    # Look for explicit experience mentions first
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*(?:in|of|working)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            return float(max(matches, key=lambda x: int(x)))
    
    # Try to calculate from work history dates (e.g., "2011-2016" or "2011 - 2016")
    # More flexible pattern to catch various date formats
    year_range_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current|ongoing|now)'
    date_matches = re.findall(year_range_pattern, text_lower)
    
    if date_matches:
        total_years = 0
        current_year = 2026
        for start, end in date_matches:
            start_year = int(start)
            if end in ['present', 'current', 'ongoing', 'now']:
                end_year = current_year
            else:
                try:
                    end_year = int(end)
                except:
                    end_year = current_year
            
            years = end_year - start_year
            # Only count reasonable work durations (not education years typically 4+ years)
            if 0 < years <= 15:
                total_years += years
        
        if total_years > 0:
            return min(total_years, 30)
    
    # Check for fresher/entry-level indicators AFTER checking dates
    fresher_indicators = ['fresher', 'entry level', 'entry-level', 'recent graduate', 'new graduate']
    if any(ind in text_lower for ind in fresher_indicators):
        return 0.5
    
    # If has internship experience, return at least 0.5
    if 'intern' in text_lower:
        return 0.5
    
    return 0.0


def extract_education(text: str) -> List[Dict[str, str]]:
    """Extract education information from resume"""
    education_list = []
    text_lower = text.lower()
    lines = text.split('\n')
    
    # Look for specific degree mentions with context
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        matched = False  # Track if this line matched a degree
        
        # B.S.B.A. detection - CHECK FIRST (before B.S. since it contains "b.s.")
        if not matched and ('b.s.b.a' in line_lower or 'bsba' in line_lower):
            field = ""
            if 'management' in line_lower or 'information' in line_lower:
                field = "Management Information Systems"
            elif 'business' in line_lower:
                field = "Business Administration"
            education_list.append({"degree": "B.S.B.A.", "field": field, "raw": line.strip()})
            matched = True
        
        # M.S. / Master's detection
        if not matched and ('m.s.' in line_lower or 'm.s.,' in line_lower or "master's" in line_lower or 
            'master of science' in line_lower or 'ms in' in line_lower or 'ms,' in line_lower):
            field = ""
            if 'computer science' in line_lower:
                field = "Computer Science"
            elif 'information' in line_lower:
                field = "Information Technology"
            elif 'data' in line_lower:
                field = "Data Science"
            education_list.append({"degree": "M.S.", "field": field, "raw": line.strip()})
            matched = True
        
        # B.S. / Bachelor's detection (after B.S.B.A. to avoid conflict)
        if not matched and ('b.s.' in line_lower or 'b.s.,' in line_lower or "bachelor's" in line_lower or
              'bachelor of science' in line_lower or 'bs in' in line_lower or 'bs,' in line_lower):
            field = ""
            if 'computer' in line_lower:
                field = "Computer Science"
            education_list.append({"degree": "B.S.", "field": field, "raw": line.strip()})
            matched = True
        
        # MBA detection
        if not matched and ('mba' in line_lower or 'm.b.a' in line_lower):
            field = ""
            if 'digital transformation' in line_lower:
                field = "Digital Transformation"
            elif 'business' in line_lower:
                field = "Business Administration"
            education_list.append({"degree": "MBA", "field": field, "raw": line.strip()})
            matched = True
        
        # B.Tech detection
        if not matched and ('b.tech' in line_lower or 'b tech' in line_lower or 'btech' in line_lower or 'b. tech' in line_lower):
            field = ""
            if 'computer' in line_lower:
                field = "Computer Engineering"
            elif 'information' in line_lower:
                field = "Information Technology"
            elif 'electronic' in line_lower:
                field = "Electronics"
            education_list.append({"degree": "B.Tech", "field": field, "raw": line.strip()})
            matched = True
        
        # M.Tech detection
        if not matched and ('m.tech' in line_lower or 'm tech' in line_lower or 'mtech' in line_lower):
            field = ""
            if 'computer' in line_lower:
                field = "Computer Science"
            education_list.append({"degree": "M.Tech", "field": field, "raw": line.strip()})
            matched = True
        
        # B.E detection (avoid matching "be" as a word)
        if not matched and re.search(r'\bb\.?e\.?\b', line_lower) and 'bachelor' not in line_lower:
            education_list.append({"degree": "B.E", "field": "", "raw": line.strip()})
            matched = True
        
        # BCA/MCA detection - use word boundaries to avoid false matches
        if not matched and re.search(r'\bbca\b', line_lower) and 'bachelor' not in line_lower:
            education_list.append({"degree": "BCA", "field": "Computer Applications", "raw": line.strip()})
            matched = True
        if not matched and re.search(r'\bmca\b', line_lower) and 'm.s.' not in line_lower and "master's" not in line_lower:
            education_list.append({"degree": "MCA", "field": "Computer Applications", "raw": line.strip()})
            matched = True
    
    # Remove duplicates
    seen = set()
    unique_edu = []
    for edu in education_list:
        key = edu['degree']
        if key not in seen:
            seen.add(key)
            unique_edu.append(edu)
    
    return unique_edu if unique_edu else [{"degree": "Degree", "field": "", "raw": ""}]


def extract_work_experience(text: str) -> List[Dict[str, Any]]:
    """Extract work experience entries from resume"""
    experiences = []
    
    # Look for company/role patterns
    # This is a simplified extraction - can be enhanced
    lines = text.split('\n')
    current_exp = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for job titles
        job_indicators = ['engineer', 'developer', 'manager', 'analyst', 'designer', 
                         'architect', 'lead', 'senior', 'junior', 'intern', 'consultant']
        
        if any(indicator in line.lower() for indicator in job_indicators):
            if current_exp:
                experiences.append(current_exp)
            current_exp = {"title": line, "description": ""}
        elif current_exp and line:
            current_exp["description"] += line + " "
    
    if current_exp:
        experiences.append(current_exp)
    
    return experiences[:5]  # Return top 5 experiences

def parse_resume(file_path: str) -> Dict[str, Any]:
    """Main function to parse resume and extract all information"""
    # Determine file type and extract text
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        raw_text = extract_text_from_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()
    
    # If no text extracted (image-based PDF), return a message
    if not raw_text or len(raw_text.strip()) < 50:
        return {
            "name": "",
            "skills": [],
            "experience_years": 0,
            "education": [],
            "work_experience": [],
            "contact_info": {},
            "raw_text": "",
            "error": "Could not extract text from PDF. The file may be image-based. Please upload a DOCX file or a text-based PDF."
        }
    
    # Extract all information
    skills = extract_skills(raw_text)
    education = extract_education(raw_text)
    experience_years = extract_experience_years(raw_text)
    
    # Format education for display
    education_display = []
    for edu in education:
        if edu.get("field"):
            education_display.append(f"{edu['degree']} in {edu['field']}")
        else:
            education_display.append(edu['degree'])
    
    return {
        "name": extract_name(raw_text),
        "skills": skills,
        "experience_years": experience_years,
        "education": education_display if education_display else ["Education info found"],
        "education_details": education,
        "work_experience": extract_work_experience(raw_text),
        "contact_info": {
            "email": extract_email(raw_text),
            "phone": extract_phone(raw_text)
        },
        "raw_text": raw_text[:5000]  # Store first 5000 chars
    }

def match_resume_to_job(parsed_resume: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    """Match parsed resume against job requirements and calculate scores"""
    
    resume_skills = [s.lower() for s in parsed_resume.get("skills", [])]
    required_skills = [s.lower() for s in job.get("required_skills", [])]
    preferred_skills = [s.lower() for s in job.get("preferred_skills", [])]
    
    # Calculate skill matches
    matched_required = [s for s in required_skills if s in resume_skills]
    matched_preferred = [s for s in preferred_skills if s in resume_skills]
    missing_skills = [s for s in required_skills if s not in resume_skills]
    
    # Calculate scores
    required_score = len(matched_required) / len(required_skills) if required_skills else 1.0
    preferred_score = len(matched_preferred) / len(preferred_skills) if preferred_skills else 0.5
    
    # Experience match
    min_exp = job.get("min_experience_years", 0)
    candidate_exp = parsed_resume.get("experience_years", 0)
    experience_match = candidate_exp >= min_exp
    experience_score = min(1.0, candidate_exp / max(min_exp, 1))
    
    # Education match
    education_reqs = job.get("education_requirements", [])
    candidate_education = [e.get("degree", "").lower() for e in parsed_resume.get("education", [])]
    education_match = not education_reqs or any(
        req.lower() in ' '.join(candidate_education) for req in education_reqs
    )
    education_score = 1.0 if education_match else 0.5
    
    # Overall match score (weighted)
    match_score = (
        required_score * 0.5 +      # 50% weight on required skills
        preferred_score * 0.15 +    # 15% weight on preferred skills
        experience_score * 0.20 +   # 20% weight on experience
        education_score * 0.15      # 15% weight on education
    ) * 100
    
    # Determine ranking
    if match_score >= 70:
        ranking = "high_match"
    elif match_score >= 40:
        ranking = "potential"
    else:
        ranking = "reject"
    
    return {
        "match_score": round(match_score, 2),
        "matched_skills": matched_required + matched_preferred,
        "missing_skills": missing_skills,
        "experience_match": experience_match,
        "education_match": education_match,
        "ranking": ranking,
        "breakdown": {
            "required_skills_score": round(required_score * 100, 2),
            "preferred_skills_score": round(preferred_score * 100, 2),
            "experience_score": round(experience_score * 100, 2),
            "education_score": round(education_score * 100, 2)
        }
    }
