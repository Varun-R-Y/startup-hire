import re

# Constants for heading detection
TARGET_HEADINGS = {
    "skills": {
        "skills", "technical skills", "key skills", "skills & technologies",
        "technologies", "expertise", "core skills", "programming languages"
    },
    "education": {
        "education", "academic background", "qualifications", "academic credentials",
        "academic profile", "academic history", "scholastic details"
    },
    "experience": {
        "experience", "work experience", "employment history", "professional experience",
        "work history", "professional background", "employment"
    },
    "projects": {
        "projects", "personal projects", "key projects", "academic projects",
        "relevant projects", "projects & publications"
    }
}

STOP_HEADINGS = {
    # Summary / Profile
    "summary", "professional summary", "objective", "career objective", "profile", "about me", "personal summary",
    # Certifications / Courses / Licenses
    "certifications", "certificates", "certifications & licenses", "courses", "training",
    "certifications & courses", "credentials", "licenses", "online courses",
    # Languages
    "languages", "languages spoken", "languages & frameworks", "language proficiency",
    # Awards / Honors / Achievements
    "awards", "honors", "achievements", "honors & awards", "key achievements", "accomplishments", "scholastic achievements",
    # Interests / Hobbies / Activities
    "interests", "hobbies", "extracurricular activities", "activities", "interests & hobbies", "hobbies & interests",
    # Publications / Patents / Research
    "publications", "patents", "research", "publications & presentations", "presentations", "articles",
    # References
    "references", "references available upon request", "recommendations",
    # Declarations / Miscellaneous
    "declarations", "declaration", "additional information", "additional details", "miscellaneous",
    "volunteer experience", "volunteering", "volunteer work", "social work", "community service",
    # Contact / Personal info
    "contact", "contact info", "personal details", "personal information", "links", "social links",
    "contact details", "about"
}


def extract_email(text: str) -> str:
    """
    Extracts the first email address found in the text.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    email_match = re.search(email_pattern, text)
    return email_match.group(0).strip() if email_match else ""


def extract_phone(text: str) -> str:
    """
    Extracts the first phone number found in the text.
    """
    phone_pattern = (
        r'(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})|'  # e.g., 123-456-7890
        r'(?:(?:\+?\d{1,3}[-.\s]?)?\d{5}[-.\s]?\d{5})|'                   # e.g., 98765-43210
        r'(?:(?:\+?\d{1,3}[-.\s]?)?\d{10})'                               # e.g., 9876543210
    )
    phone_match = re.search(phone_pattern, text)
    return phone_match.group(0).strip() if phone_match else ""


def extract_name(text: str) -> str:
    """
    Extracts the candidate's full name, assumed to be the first non-empty line.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def extract_sections(text: str) -> dict:
    """
    Extracts section contents for Skills, Education, Experience, and Projects.
    Capture is stopped as soon as another section heading or non-target heading is detected.
    """
    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "projects": []
    }

    current_section = None

    for line in text.splitlines():
        # Clean the line of leading formatting like bullet characters, numbers, and spaces
        clean_line = re.sub(r'^[\s\-\*\d\.\)]+', '', line).strip()
        # Keep only lowercase letters, digits, whitespace, and ampersands
        norm = re.sub(r'[^a-z0-9&\s]', '', clean_line.lower()).strip()

        # Check if the line matches any target section heading
        found_target_section = None
        for sec_key, headings in TARGET_HEADINGS.items():
            if norm in headings:
                found_target_section = sec_key
                break

        if found_target_section:
            current_section = found_target_section
        elif norm in STOP_HEADINGS:
            # Stop capture when an unrecognized section heading appears
            current_section = None
        elif current_section is not None:
            sections[current_section].append(line.strip())

    return {
        "skills": "\n".join(sections["skills"]).strip(),
        "education": "\n".join(sections["education"]).strip(),
        "experience": "\n".join(sections["experience"]).strip(),
        "projects": "\n".join(sections["projects"]).strip()
    }


def parse_resume_text(text: str) -> dict:
    """
    Parses plain text from a resume to extract key sections and contact details.

    Args:
        text (str): The raw text extracted from the candidate's resume PDF.

    Returns:
        dict: A dictionary containing the following keys:
            - full_name (str)
            - email (str)
            - phone (str)
            - skills (str)
            - education (str)
            - experience (str)
            - projects (str)
    """
    text = text.replace("\r\n", "\n")
    sections = extract_sections(text)
    return {
        "full_name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        **sections
    }
