import re
from typing import Dict, Any, List, Set, Optional

# Comprehensive Technical Skill Taxonomy
TECH_SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "Go", "Golang",
        "Rust", "Kotlin", "Swift", "Dart", "R", "PHP", "Ruby", "Scala", "Perl", "Bash", "Shell", "SQL"
    ],
    "Frameworks & Libraries": [
        "React", "React.js", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js",
        "Node.js", "Express", "Express.js", "Django", "Flask", "FastAPI",
        "Spring Boot", "Spring", "ASP.NET", ".NET", ".NET Core",
        "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Pandas", "NumPy",
        "OpenCV", "NLTK", "Spacy", "HuggingFace", "Tailwind CSS", "Bootstrap",
        "jQuery", "Hibernate"
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Oracle Database",
        "Redis", "Cassandra", "Firebase", "DynamoDB", "MariaDB", "Elasticsearch", "MS SQL Server"
    ],
    "Web Technologies": [
        "HTML", "HTML5", "CSS", "CSS3", "REST API", "GraphQL", "WebSockets",
        "JSON", "XML", "SOAP", "AJAX", "Responsive Design"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Microsoft Azure", "Azure", "Google Cloud", "GCP",
        "Docker", "Kubernetes", "Git", "GitHub", "GitLab", "CI/CD", "Jenkins",
        "Linux", "Unix", "Terraform", "Ansible", "Kubernetes", "Nginx", "Microservices"
    ],
    "Machine Learning & AI": [
        "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP",
        "Computer Vision", "Data Science", "Artificial Intelligence", "AI",
        "Large Language Models", "LLM", "Generative AI", "Neural Networks",
        "Supervised Learning", "Unsupervised Learning", "Data Mining", "Predictive Modeling"
    ],
    "Data Analytics & BI": [
        "Data Analysis", "Power BI", "Tableau", "Excel", "Data Visualization",
        "Matplotlib", "Seaborn", "Statistics", "Data Warehousing", "ETL", "Big Data", "Hadoop", "Spark"
    ],
    "Core Technical Concepts": [
        "Data Structures", "Algorithms", "Object-Oriented Programming", "OOP",
        "System Design", "Operating Systems", "Computer Networks", "Database Management Systems", "DBMS",
        "Problem Solving", "Software Engineering", "Design Patterns", "Agile", "Scrum"
    ],
    "Tools & Platforms": [
        "VS Code", "Visual Studio", "IntelliJ IDEA", "PyCharm", "Jupyter Notebook",
        "Postman", "Jira", "Figma", "Eclipse", "Android Studio"
    ]
}

# Flattened lookup mapping normalized skill -> canonical name
CANONICAL_SKILL_MAP: Dict[str, str] = {}
for category, skills in TECH_SKILLS_TAXONOMY.items():
    for skill in skills:
        CANONICAL_SKILL_MAP[skill.lower()] = skill

# Additional common aliases
SKILL_ALIASES: Dict[str, str] = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "cpp": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "c sharp": "C#",
    "reactjs": "React",
    "react.js": "React",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "expressjs": "Express",
    "vuejs": "Vue",
    "angularjs": "Angular",
    "nextjs": "Next.js",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "k8s": "Kubernetes",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "powerbi": "Power BI",
    "dsa": "Data Structures",
    "data structures and algorithms": "Data Structures",
    "oops": "Object-Oriented Programming",
    "oop": "Object-Oriented Programming",
    "dbms": "DBMS",
    "restful api": "REST API",
    "rest apis": "REST API",
    "rest api": "REST API"
}

def extract_name(text: str) -> str:
    """Extract candidate candidate name from resume header lines."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Unknown Candidate"
    
    # Filter out common header words
    ignored_patterns = [
        r'^(curriculum\s+vitae|resume|biodata|profile|contact|summary)$',
        r'^(page\s+\d+|personal\s+details|personal\s+information)$',
        r'^(email|phone|mobile|tel|address|linkedin|github)'
    ]
    
    for line in lines[:5]:
        if any(re.match(pat, line, re.IGNORECASE) for pat in ignored_patterns):
            continue
        # Names typically have 2-4 words, alphabet only, length 3-40
        clean_line = re.sub(r'[^a-zA-Z\s\.]', '', line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4 and 4 <= len(clean_line) <= 40:
            if not any(w.lower() in ["developer", "engineer", "student", "intern", "curriculum", "vitae", "resume"] for w in words):
                return clean_line
                
    # Fallback to first line if reasonably short
    if lines:
        first_line = re.sub(r'[^a-zA-Z\s]', '', lines[0]).strip()
        if 3 <= len(first_line) <= 35:
            return first_line

    return "Unknown Candidate"

def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract email, phone, LinkedIn, GitHub links."""
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+91[-.\s]?[6-9]\d{9}', text)
    linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    github_match = re.search(r'github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)

    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None
    }

def extract_education(text: str) -> Dict[str, Any]:
    """Extract degree, branch/department, college/university, and CGPA/percentage."""
    degree = None
    branch = None
    college = None
    cgpa = None

    # CGPA / Percentage regex
    cgpa_match = re.search(r'(?:cgpa|gpa|score|grade)[:\s]*([0-9]\.[0-9]{1,2}(?:\s*/\s*10(?:\.0)?)?)', text, re.IGNORECASE)
    if not cgpa_match:
        cgpa_match = re.search(r'\b([0-9]\.[0-9]{1,2})\s*/\s*10\b', text, re.IGNORECASE)
    if cgpa_match:
        cgpa = cgpa_match.group(1).replace("/10.0", "").replace("/10", "").strip()
    else:
        # Check percentage
        pct_match = re.search(r'([6-9][0-9](?:\.[0-9]{1,2})?)\s*%', text)
        if pct_match:
            cgpa = f"{pct_match.group(1)}%"

    # Degrees
    degree_patterns = [
        (r'\b(B\.?\s*Tech(?:\.|\b)|Bachelor of Technology)\b', "B.Tech"),
        (r'\b(B\.?\s*E(?:\.|\b)|Bachelor of Engineering)\b', "B.E."),
        (r'\b(M\.?\s*Tech(?:\.|\b)|Master of Technology)\b', "M.Tech"),
        (r'\b(B\.?\s*C\.?\s*A(?:\.|\b)|Bachelor of Computer Applications)\b', "BCA"),
        (r'\b(M\.?\s*C\.?\s*A(?:\.|\b)|Master of Computer Applications)\b', "MCA"),
        (r'\b(B\.?\s*Sc(?:\.|\b)|Bachelor of Science)\b', "B.Sc"),
        (r'\b(M\.?\s*Sc(?:\.|\b)|Master of Science)\b', "M.Sc")
    ]
    for pattern, d_name in degree_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            degree = d_name
            break

    # Branch / Department
    branch_patterns = [
        (r'Computer Science(?: and Engineering)?|CSE', "Computer Science and Engineering"),
        (r'Information Technology|IT', "Information Technology"),
        (r'Electronics and Communication(?: Engineering)?|ECE', "Electronics and Communication Engineering"),
        (r'Electrical and Electronics(?: Engineering)?|EEE', "Electrical and Electronics Engineering"),
        (r'Artificial Intelligence(?: and Data Science)?|AI & DS|AI/ML', "Artificial Intelligence and Data Science"),
        (r'Data Science', "Data Science"),
        (r'Mechanical Engineering|ME', "Mechanical Engineering"),
        (r'Civil Engineering|CE', "Civil Engineering")
    ]
    for pattern, b_name in branch_patterns:
        if re.search(rf'\b({pattern})\b', text, re.IGNORECASE):
            branch = b_name
            break

    # College / University
    college_match = re.search(
        r'([A-Za-z\s&]+(?:College of Engineering|Institute of Technology|University|Engineering College|Polytechnic|Institute of Science|Academy of Higher Education))',
        text, re.IGNORECASE
    )
    if college_match:
        college = college_match.group(1).strip()
        # Clean up college string length
        if len(college) > 60:
            college = college[:60] + "..."

    return {
        "degree": degree or "Not explicitly specified",
        "branch": branch or "Not explicitly specified",
        "college": college or "Not explicitly specified",
        "cgpa": cgpa or "Not explicitly specified"
    }

def extract_skills(text: str) -> Dict[str, Any]:
    """
    Extract technical skills from text using taxonomy and pattern matching.
    Returns categorized skills and a unified set of detected skills.
    """
    text_lower = text.lower()
    categorized: Dict[str, List[str]] = {}
    all_skills_found: Set[str] = set()

    for category, skill_list in TECH_SKILLS_TAXONOMY.items():
        found_in_category = []
        for skill in skill_list:
            skill_lower = skill.lower()
            # Boundary-aware matching
            # Handle special characters like C++, C#, .NET
            escaped = re.escape(skill_lower)
            if skill_lower in ["c", "r"]:
                # Single letter needs strict boundary
                pattern = rf'(?:\b|[\s,/]){escaped}(?:\b|[\s,/])'
            elif "+" in skill_lower or "#" in skill_lower or "." in skill_lower:
                pattern = rf'(?:^|[\s,;/()|-]){escaped}(?:$|[\s,;/()|-])'
            else:
                pattern = rf'\b{escaped}\b'

            if re.search(pattern, text_lower):
                found_in_category.append(skill)
                all_skills_found.add(skill)

        if found_in_category:
            categorized[category] = sorted(list(set(found_in_category)))

    # Also check aliases
    for alias, canonical in SKILL_ALIASES.items():
        escaped_alias = re.escape(alias)
        pattern = rf'\b{escaped_alias}\b' if not ("+" in alias or "#" in alias or "." in alias) else rf'(?:^|[\s,;/()|-]){escaped_alias}(?:$|[\s,;/()|-])'
        if re.search(pattern, text_lower):
            all_skills_found.add(canonical)
            # Find category for canonical
            for cat, sk_list in TECH_SKILLS_TAXONOMY.items():
                if canonical in sk_list:
                    if cat not in categorized:
                        categorized[cat] = []
                    if canonical not in categorized[cat]:
                        categorized[cat].append(canonical)

    return {
        "categorized_skills": categorized,
        "all_skills": sorted(list(all_skills_found)),
        "total_skills_count": len(all_skills_found)
    }

def extract_sections(text: str) -> Dict[str, str]:
    """Split resume into common sections like Education, Experience, Projects, Certifications."""
    section_headers = [
        ("education", r'(?:education|academic\s+background|academics|qualifications)'),
        ("experience", r'(?:experience|internships|work\s+experience|employment\s+history|professional\s+experience)'),
        ("projects", r'(?:projects|academic\s+projects|personal\s+projects|key\s+projects)'),
        ("certifications", r'(?:certifications|certificates|licenses|courses\s+completed)'),
        ("skills", r'(?:technical\s+skills|skills|technologies|competencies|areas\s+of\s+expertise)'),
        ("achievements", r'(?:achievements|accomplishments|awards|honors|extracurricular)')
    ]

    # Find offsets of section headers
    matches = []
    for s_name, pat in section_headers:
        for m in re.finditer(rf'(?:\n|\A)\s*(?:[#*-]\s*)?({pat})\s*[:\n]', text, re.IGNORECASE):
            matches.append((m.start(), m.group(1), s_name))

    matches.sort(key=lambda x: x[0])

    sections: Dict[str, str] = {}
    if not matches:
        return sections

    for i in range(len(matches)):
        start = matches[i][0]
        s_name = matches[i][2]
        end = matches[i+1][0] if i + 1 < len(matches) else len(text)
        sections[s_name] = text[start:end].strip()

    return sections

def extract_projects(text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Extract project titles, technologies used, and description highlights."""
    proj_text = sections.get("projects", "")
    if not proj_text:
        # Check if text contains project section mentions
        m = re.search(r'(?:projects|academic projects)([\s\S]{100,1000}?)(?:education|skills|certifications|experience|\Z)', text, re.IGNORECASE)
        if m:
            proj_text = m.group(1)

    if not proj_text:
        return []

    projects = []
    # Project items typically preceded by bullets or bold/capitalized lines
    lines = [l.strip() for l in proj_text.split("\n") if l.strip()]
    current_proj: Optional[Dict[str, Any]] = None

    for line in lines[1:]:  # skip header
        # Check if line looks like a title
        is_title = (
            (line.startswith("-") or line.startswith("•") or line.startswith("*") or len(line) < 60)
            and not line.lower().startswith("tools:")
            and not line.lower().startswith("technologies:")
            and not line.lower().startswith("description:")
        )

        # Detect technologies mentioned in line
        techs_in_line = [sk for sk in CANONICAL_SKILL_MAP.values() if re.search(rf'\b{re.escape(sk)}\b', line, re.IGNORECASE)]

        if is_title and len(projects) < 5:
            clean_title = re.sub(r'^[•\-\*#]+\s*', '', line).strip()
            # Ignore if generic
            if len(clean_title) > 4 and not clean_title.lower().startswith("project"):
                current_proj = {
                    "title": clean_title[:60],
                    "technologies": list(set(techs_in_line)),
                    "description": ""
                }
                projects.append(current_proj)
        elif current_proj:
            if techs_in_line:
                current_proj["technologies"] = list(set(current_proj["technologies"] + techs_in_line))
            if not current_proj["description"] and len(line) > 20:
                current_proj["description"] = line[:120]

    return projects[:4]

def extract_experience(text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Extract internship or work experience entries."""
    exp_text = sections.get("experience", "")
    if not exp_text:
        return []

    experiences = []
    lines = [l.strip() for l in exp_text.split("\n") if l.strip()]
    for line in lines[1:]:
        if re.search(r'\b(intern|internship|developer|trainee|analyst|engineer|associate)\b', line, re.IGNORECASE):
            experiences.append({
                "role_or_company": re.sub(r'^[•\-\*#]+\s*', '', line)[:70],
                "details": ""
            })
        elif experiences and not experiences[-1]["details"] and len(line) > 20:
            experiences[-1]["details"] = line[:100]

    return experiences[:4]

def extract_certifications(text: str, sections: Dict[str, str]) -> List[str]:
    """Extract certifications names."""
    cert_text = sections.get("certifications", "")
    certs = []
    if cert_text:
        lines = [l.strip() for l in cert_text.split("\n") if l.strip()]
        for line in lines[1:]:
            clean_line = re.sub(r'^[•\-\*#]+\s*', '', line).strip()
            if 5 < len(clean_line) < 80:
                certs.append(clean_line)
    else:
        # Search for known cert patterns
        cert_patterns = [
            r'AWS Certified [A-Za-z\s]+',
            r'Azure Fundamentals|Microsoft Certified [A-Za-z\s]+',
            r'Google Cloud Certified [A-Za-z\s]+',
            r'Oracle Certified [A-Za-z\s]+',
            r'Cisco Certified [A-Za-z\s]+|CCNA',
            r'HackerRank [A-Za-z\s]+ Certificate',
            r'Coursera [A-Za-z\s]+ Specialization'
        ]
        for pat in cert_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                certs.append(m.group(0).strip())

    return list(dict.fromkeys(certs))[:5]

def analyze_resume_quality(
    text: str,
    contact_info: Dict[str, Any],
    education: Dict[str, Any],
    skills_data: Dict[str, Any],
    projects: List[Dict[str, Any]],
    experience: List[Dict[str, Any]],
    certifications: List[str]
) -> Dict[str, Any]:
    """
    Perform qualitative inspection of resume structure and content.
    Returns clear, evidence-based improvement suggestions without unverified claims.
    """
    observations = []
    improvements = []
    score_points = 0
    max_points = 100

    # 1. Contact Information (15 pts)
    if contact_info.get("email") and contact_info.get("phone"):
        score_points += 15
        observations.append("Complete contact details provided (Email and Phone).")
    elif contact_info.get("email") or contact_info.get("phone"):
        score_points += 8
        improvements.append("Your resume could be improved by providing both a verified email address and telephone contact.")
    else:
        improvements.append("Your resume could be improved by including clear contact information (Email and Phone) in the header.")

    # 2. Education (15 pts)
    if education.get("degree") != "Not explicitly specified":
        score_points += 10
        observations.append(f"Clear degree qualification specified: {education.get('degree')}.")
    else:
        improvements.append("Your resume could be improved by clearly specifying your degree title and department/branch.")

    if education.get("cgpa") != "Not explicitly specified":
        score_points += 5
        observations.append(f"Academic CGPA/Score explicitly mentioned ({education.get('cgpa')}).")
    else:
        improvements.append("Your resume could be improved by mentioning your graduation CGPA or academic percentage for campus eligibility screening.")

    # 3. Technical Skills (25 pts)
    total_skills = skills_data.get("total_skills_count", 0)
    if total_skills >= 8:
        score_points += 25
        observations.append(f"Strong technical skill breadth ({total_skills} distinct technical skills detected).")
    elif total_skills >= 4:
        score_points += 15
        improvements.append("Your resume could be improved by expanding your technical skill listing with relevant frameworks and tools.")
    else:
        score_points += 5
        improvements.append("Your resume contains very few recognized technical skills. Adding concrete languages, frameworks, and databases is strongly recommended.")

    # 4. Projects (20 pts)
    if len(projects) >= 2:
        score_points += 20
        observations.append(f"Contains multiple technical project entries ({len(projects)} projects identified).")
    elif len(projects) == 1:
        score_points += 10
        improvements.append("Your resume could be improved by showcasing at least 2-3 substantive technical projects.")
    else:
        improvements.append("Your resume could be improved by adding a dedicated 'Projects' section highlighting real-world implementations.")

    # Check for quantifiable project metrics (e.g., numbers, percentages)
    has_metrics = bool(re.search(r'\b(?:\d+%\s*|\d+x\s*|\$\d+|\d+\s*users|\d+\s*ms|\d+\s*seconds)\b', text, re.IGNORECASE))
    if has_metrics:
        observations.append("Contains quantifiable impact indicators (percentages, metrics, or performance outcomes).")
    else:
        improvements.append("Your resume could be improved by incorporating quantifiable results into project bullet points (e.g., 'reduced latency by 30%', 'handled 500+ requests').")

    # 5. Experience / Internships (15 pts)
    if len(experience) > 0:
        score_points += 15
        observations.append("Practical internship/work experience included.")
    else:
        score_points += 5
        improvements.append("Your resume could be improved by featuring industry internships, academic research experience, or open-source contributions.")

    # 6. Certifications (10 pts)
    if len(certifications) > 0:
        score_points += 10
        observations.append(f"Professional credentials or certifications listed ({len(certifications)} found).")
    else:
        score_points += 3
        improvements.append("Your resume could be improved by adding industry-standard certifications (e.g., Cloud, Database, or Programming credentials).")

    return {
        "quality_score": min(100, max(10, score_points)),
        "observations": observations,
        "improvements": improvements
    }

def extract_resume_information(raw_text: str, filename: str = "") -> Dict[str, Any]:
    """
    Extract comprehensive structured information from resume text.
    Factual extraction only; does not invent unmentioned details.
    """
    if not raw_text or len(raw_text.strip()) == 0:
        return {
            "status": "error",
            "message": "Empty resume text provided for information extraction."
        }

    contact = extract_contact_info(raw_text)
    name = extract_name(raw_text)
    education = extract_education(raw_text)
    skills = extract_skills(raw_text)
    sections = extract_sections(raw_text)
    projects = extract_projects(raw_text, sections)
    experience = extract_experience(raw_text, sections)
    certifications = extract_certifications(raw_text, sections)
    quality = analyze_resume_quality(raw_text, contact, education, skills, projects, experience, certifications)

    return {
        "status": "success",
        "personal": {
            "name": name,
            "contact": contact
        },
        "education": education,
        "technical_skills": skills["categorized_skills"],
        "all_skills": skills["all_skills"],
        "total_skills_count": skills["total_skills_count"],
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "quality_analysis": quality,
        "has_projects": len(projects) > 0,
        "has_experience": len(experience) > 0,
        "filename": filename
    }
