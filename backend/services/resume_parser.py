import pdfplumber
import re
from typing import Dict, Any
import io

def parse_resume(pdf_bytes: bytes) -> Dict[str, Any]:
    full_text = ""
    pdf_stream = io.BytesIO(pdf_bytes)
    
    try:
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    full_text += extracted + "\n"
    except Exception as e:
        raise ValueError(f"Could not read resume PDF: {str(e)}")

    full_text = full_text.replace("\r\n", "\n").strip()
    
    sections = {
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "certifications": ""
    }
    
    if not full_text:
        return {"full_text": "", "sections": sections}

    # Normalize text for regex searching
    lines = full_text.split('\n')
    
    # Regex patterns for section headers
    patterns = {
        "skills": re.compile(r'^(skills|technical skills|core competencies)', re.IGNORECASE),
        "experience": re.compile(r'^(experience|work history|employment|internship|professional experience)', re.IGNORECASE),
        "projects": re.compile(r'^(projects|personal projects|academic projects)', re.IGNORECASE),
        "education": re.compile(r'^(education|academic background)', re.IGNORECASE),
        "certifications": re.compile(r'^(certifications|courses|licenses)', re.IGNORECASE)
    }

    current_section = None
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        matched_section = None
        for section, pattern in patterns.items():
            if pattern.match(cleaned_line):
                matched_section = section
                break
                
        if matched_section:
            current_section = matched_section
        elif current_section:
            sections[current_section] += line + "\n"

    # Strip excessive whitespace from sections
    for k in sections:
        sections[k] = sections[k].strip()

    return {
        "full_text": full_text,
        "sections": sections
    }
