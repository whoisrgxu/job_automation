"""
Resume customization prompts based on job category.
Exports prompts and section configurations for SDE and Support jobs.
"""

# ---------- SECTION STYLES (same for both categories) ----------
SECTION_STYLES = {
    "SUMMARY": "SummaryStyle",
    "SKILLS": "SkillStyle",
    "HOOPP_EXPERIENCE": "BulletStyle",
    "PORTFOLIO_TRACKER": "BulletStyle",
    "JOBPILOT": "BulletStyle",
}

# ---------- SECTION RULES FOR SDE JOBS ----------
SDE_SECTION_RULES = {
    "SUMMARY": """
    - Keep short (2–3 sentences).
    - Highlight only most relevant 3-4 technologies and 2-3 soft skills.
    - Professional profile tone.
    """,
    "SKILLS": """
    - Present as a **category:** skill1, skill2 format, and no more than 5 categories.
    - Delete irrelevant skills.
    - Category name has to be wrapped with "**" but do not wrap any specific skills in ** ... **.
    """,
    "HOOPP_EXPERIENCE": """
    - Rewrite into no more than 6 bullet points and no more than 170 words total.
    - You can delete irrelevant items and update or expand existing items.
    - Ensure the bullets remain coherent with a co-op/internship context, not senior-level responsibilities.
    - Highlight required skills from the job description, but naturally (not forced).
    - If suitable, cover at least 90 percent of important required skills not already covered by the JobPilot or Portfolio Tracker sections.
    - Maintain professional resume tone and readability.
    """,
    "JOBPILOT": """
    - No more than 5 items.
    - No more than 4 items and no more than 105 words.
    """,
    "PORTFOLIO_TRACKER": """
    - No more than 4 items and no more than 130 words.
    """,
}

# ---------- SECTION RULES FOR CLOUD SUPPORT JOBS (no JOBPILOT or PORTFOLIO_TRACKER) ----------
CLOUD_SUPPORT_SECTION_RULES = {
    "SUMMARY": """
    - Keep short (2–3 sentences).
    - Highlight only most relevant 3-4 technologies and 2-3 soft skills.
    - Professional profile tone.
    """,
    "SKILLS": """
    - Format as **Category:** skill1, skill2, skill3.
    - No more than 5 skill categories.
    - Category names must be wrapped with "**".
    - Do not wrap individual skills.
    - Remove irrelevant SDE-heavy skills.
    """,
    "HOOPP_EXPERIENCE": """
    - Rewrite into no more than 6 bullet points and no more than 170 words total.
    - You can delete irrelevant items and update or expand existing items.
    - Ensure the bullets remain coherent with a co-op/internship context, not senior-level responsibilities.
    - Highlight required skills from the job description, but naturally (not forced).
    - If suitable, cover at least 80 percent of the important required skills.
    - Maintain professional resume tone and readability.
    """
}
# ---------- SECTION RULES FOR APPLICATION SUPPORT JOBS (no JOBPILOT or PORTFOLIO_TRACKER) ----------
APPLICATION_SUPPORT_SECTION_RULES = {
    "SUMMARY": """
    - Keep short (2–3 sentences).
    - Highlight only most relevant 3-4 technologies and 2-3 soft skills.
    - Professional profile tone.
    """,
    "SKILLS": """
    - Format as **Category:** skill1, skill2, skill3.
    - Use no more than 5 categories.
    - Category names wrapped in "**"; individual skills are not wrapped.
    - Remove irrelevant SDE-oriented skills.
    """,
    "HOOPP_EXPERIENCE": """
    - Rewrite into no more than 6 bullet points and no more than 170 words total.
    - You can delete irrelevant items and update or expand existing items.
    - Ensure the bullets remain coherent with a co-op/internship context, not senior-level responsibilities.
    - Highlight required skills from the job description, but naturally (not forced).
    - If suitable, cover at least 80 percent of important required skills.
    - Maintain professional resume tone and readability.
    """
}
# ---------- SECTION RULES FOR SHAREPOINT SUPPORT JOBS (no JOBPILOT or PORTFOLIO_TRACKER) ----------
SHAREPOINT_SUPPORT_SECTION_RULES = {
    "SUMMARY": """
    - Keep short (2–3 sentences).
    - Highlight only most relevant 3-4 technologies and 2-3 soft skills.
    - Professional profile tone.
    """,
    "SKILLS": """
    - Use **Category:** skill1, skill2 formatting.
    - Max 5 categories.
    - Category names wrapped in "**", individual skills not wrapped.
    """,
    "HOOPP_EXPERIENCE": """
    - Rewrite into no more than 6 bullet points and no more than 170 words total.
    - You can delete irrelevant items and update or expand existing items.
    - Ensure the bullets remain coherent with a co-op/internship context, not senior-level responsibilities.
    - Highlight required skills from the job description, but naturally (not forced).
    - If suitable, cover at least 80 percent of important required skills.
    - Maintain professional resume tone and readability.
    """
}

# ---------- GENERAL RULES FOR SDE JOBS (original) ----------
SDE_GENERAL_RULES = """
- Keep most of the existing content and reframe if needed. Can delete irrelevant items.
- Emphasize alignment with the job description by highlighting overlapping skills and responsibilities.
- Wrap important keywords (skills, technologies, frameworks, certifications, job-critical terms) with ** ... ** so they can be processed later.
- You may integrate 2–4 additional skills from the job description that are not currently in the resume, but only if they fit naturally into the context.
- Distribution of new skills is flexible:
* Some may appear in Experience and Projects
* Some may overlap across sections if appropriate
* It is not required to use all missing skills
- Slight exaggeration of existing skills is acceptable, but do not fabricate unrelated skills.
- Keep the tone professional, concise, and ATS-friendly.
- If multiple achievements/items are needed, place each on a new paragraph (double line break) without bullet symbols.
- Output must be strictly valid JSON, no commentary.
"""

# ---------- GENERAL RULES FOR SUPPORT JOBS (modified for support roles) ----------
CLOUD_SUPPORT_GENERAL_RULES = """
- Keep most of the existing content and reframe if needed. Can delete irrelevant items.
- Emphasize alignment with the job description by highlighting overlapping skills and responsibilities.
- Wrap important keywords (skills, technologies, frameworks, certifications, job-critical terms) with ** ... ** so they can be processed later.
- You may integrate 2–4 additional skills from the job description that are not currently in the resume, but only if they fit naturally into the context of the section.
- It is not required to use all missing skills
- Slight exaggeration of existing skills is acceptable, but do not fabricate unrelated skills.
- Keep the tone professional, concise, and ATS-friendly.
- If multiple achievements/items are needed, place each on a new paragraph (double line break) without bullet symbols.
- Output must be strictly valid JSON, no commentary.
"""
APPLICATION_SUPPORT_GENERAL_RULES = """
- Keep most of the existing content and reframe if needed. Can delete irrelevant items.
- Emphasize alignment with the job description by highlighting overlapping skills and responsibilities.
- Wrap important keywords (skills, technologies, frameworks, certifications, job-critical terms) with ** ... ** so they can be processed later.
- You may integrate 2–4 additional skills from the job description that are not currently in the resume, but only if they fit naturally into the context of the section.
- It is not required to use all missing skills
- Slight exaggeration of existing skills is acceptable, but do not fabricate unrelated skills.
- Keep the tone professional, concise, and ATS-friendly.
- If multiple achievements/items are needed, place each on a new paragraph (double line break) without bullet symbols.
- Output must be strictly valid JSON, no commentary.
"""
SHAREPOINT_SUPPORT_GENERAL_RULES = """
- Keep most of the existing content and reframe if needed. Can delete irrelevant items.
- Emphasize alignment with the job description by highlighting overlapping skills and responsibilities.
- Wrap important keywords (skills, technologies, frameworks, certifications, job-critical terms) with ** ... ** so they can be processed later.
- You may integrate 2–4 additional skills from the job description that are not currently in the resume, but only if they fit naturally into the context of the section.
- It is not required to use all missing skills
- Slight exaggeration of existing skills is acceptable, but do not fabricate unrelated skills.
- Keep the tone professional, concise, and ATS-friendly.
- If multiple achievements/items are needed, place each on a new paragraph (double line break) without bullet symbols.
- Output must be strictly valid JSON, no commentary.
"""


def get_section_rules(job_category: str) -> dict:
    """
    Get section rules based on job category.
    
    Args:
        job_category: "sde" or "support"
    
    Returns:
        Dictionary of section rules
    """
    if job_category == "application_support":
        return APPLICATION_SUPPORT_SECTION_RULES
    if job_category == "cloud_support":
        return CLOUD_SUPPORT_SECTION_RULES
    if job_category == "sharepoint_support":
        return SHAREPOINT_SUPPORT_SECTION_RULES
    else:  # Default to SDE
        return SDE_SECTION_RULES


def get_sections_for_category(job_category: str) -> list:
    """
    Get list of sections to include based on job category.
    
    Args:
        job_category: "sde" or "support"
    
    Returns:
        List of section names
    """
    if job_category in ("application_support", "cloud_support", "sharepoint_support"):
        return ["SUMMARY", "SKILLS", "HOOPP_EXPERIENCE"]
    else:  # Default to SDE
        return ["SUMMARY", "SKILLS", "HOOPP_EXPERIENCE", "PORTFOLIO_TRACKER", "JOBPILOT"]


def get_general_rules(job_category: str) -> str:
    """
    Get general rules based on job category.
    
    Args:
        job_category: "sde" or "support"
    
    Returns:
        General rules string
    """
    if job_category == "application_support":
        return APPLICATION_SUPPORT_GENERAL_RULES
    if job_category == "cloud_support":
        return CLOUD_SUPPORT_GENERAL_RULES
    if job_category == "sharepoint_support":
        return SHAREPOINT_SUPPORT_GENERAL_RULES
    else:  # Default to SDE
        return SDE_GENERAL_RULES


def build_prompt(section_texts: dict, job_description: str, job_category: str = "sde", additional_info: str = None) -> str:
    """
    Build the LLM prompt for resume customization based on job category.
    
    Args:
        section_texts: Dictionary of section names to their content
        job_description: The job description text
        job_category: "sde" or "support"
        additional_info: Optional additional requirements
    
    Returns:
        The complete prompt string
    """
    # Get sections, rules, and general rules for this category
    sections_to_include = get_sections_for_category(job_category)
    section_rules = get_section_rules(job_category)
    general_rules = get_general_rules(job_category)
    
    # Filter section_texts to only include relevant sections
    filtered_sections = {k: v for k, v in section_texts.items() if k in sections_to_include}
    
    # Build sections string
    sections_str = "\n\n".join(
        f"{name}:\n{content}" for name, content in filtered_sections.items()
    )
    
    # Build rules string
    rules_str = "\n".join(
        f"- {name}: {rule.strip()}" for name, rule in section_rules.items()
    )
    
    # Build JSON format string
    json_format = "{\n"
    for section in sections_to_include:
        json_format += f'    "{section}": "...",\n'
    json_format = json_format.rstrip(",\n") + "\n}"
    
    prompt = f"""
    You are a professional resume writer.
    You will receive a job description and multiple resume sections.
    Your task is to improve each section according to the general rules and its unique rules.

    General Rules (apply to all sections):
    {general_rules}

    Unique Rules per Section:
    {rules_str}

    Job Description:
    {job_description}

    Sections:
    {sections_str}

    Additional Requirement (if any):
    {additional_info if additional_info else 'None'}

    Return JSON in this format:
    {json_format}
    """
    
    return prompt.strip()

