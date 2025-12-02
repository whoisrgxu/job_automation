# resume_customizer.py
# from openai import OpenAI
import os, json
from docx import Document
# from dotenv import load_dotenv
import re
from docx.oxml import OxmlElement
from LLMClients.clients import Model
from job_description_cleaner.jd_cleaning import clean_job_description
# ---------- CONFIG ----------
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# MODEL = "gpt-5-mini"   # or "gpt-5-mini"

# ---------- STYLE MAPPING ----------
# These names must match the style names in your Word template!
SECTION_STYLES = {
    "SUMMARY": "SummaryStyle",
    "SKILLS": "SkillStyle",
    "HOOPP_EXPERIENCE": "BulletStyle",
    "PORTFOLIO_TRACKER": "BulletStyle",
    "JOBPILOT": "BulletStyle",
}

# ---------- UNIQUE RULES ----------
SECTION_RULES = {
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
    - If possible, cover at least 90 percent of important required skills not already covered by the JobPilot or Portfolio Tracker sections.
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

# ---------- LLM HELPER ----------
import time
from typing import Dict, Optional

from openai import APIError, RateLimitError

MAX_LLM_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "4"))
BACKOFF_BASE_SECONDS = float(os.getenv("LLM_BACKOFF_BASE", "1.5"))


def _call_llm_with_retries(prompt: str) -> Optional[str]:
    for attempt in range(MAX_LLM_RETRIES + 1):
        try:
            client = Model("OPENAI", prompt)
            response = client.get_response_from_client()
            return response
        except (RateLimitError, APIError) as exc:
            if attempt == MAX_LLM_RETRIES:
                print(f"⚠️ LLM call failed after {MAX_LLM_RETRIES + 1} attempts: {exc}")
                return None
            sleep_seconds = BACKOFF_BASE_SECONDS * (2 ** attempt)
            print(f"⚠️ LLM call failed (attempt {attempt + 1}/{MAX_LLM_RETRIES + 1}): {exc}. Retrying in {sleep_seconds:.1f}s...")
            time.sleep(sleep_seconds)
        except Exception as exc:
            print(f"⚠️ Unexpected LLM error: {exc}")
            return None


def improve_resume_json(section_texts: Dict[str, str], job_description: str, additional_info: Optional[str] = None) -> Dict[str, str]:
    """Ask LLM to improve all resume sections in one JSON response."""
    # Build the big prompt
    sections_str = "\n\n".join(
        f"{name}:\n{content}" for name, content in section_texts.items()
    )
    rules_str = "\n".join(
        f"- {name}: {rule.strip()}" for name, rule in SECTION_RULES.items()
    )

    prompt = f"""
    You are a professional resume writer.
    You will receive a job description and multiple resume sections.
    Your task is to improve each section according to the general rules and its unique rules.

    General Rules (apply to all sections):
    - Keep most of the existing content and reframe if needed. Can delete irrelevant items.
    - Emphasize alignment with the job description by highlighting overlapping skills and responsibilities.
    - Wrap important keywords (skills, technologies, frameworks, certifications, job-critical terms) with ** ... ** so they can be processed later.
    - You may integrate 2–4 additional skills from the job description that are not currently in the resume, but only if they fit naturally into the context of the section.
    - Distribution of new skills is flexible:
    * Some may appear in Experience and Projects
    * Some may overlap across sections if appropriate
    * It is not required to use all missing skills
    - Slight exaggeration of existing skills is acceptable, but do not fabricate unrelated skills.
    - Keep the tone professional, concise, and ATS-friendly.
    - If multiple achievements/items are needed, place each on a new paragraph (double line break) without bullet symbols.
    - Output must be strictly valid JSON, no commentary.

    Unique Rules per Section:
    {rules_str}

    Job Description:
    {job_description}

    Sections:
    {sections_str}

    Additional Requirement (if any):
    {additional_info if additional_info else 'None'}

    Return JSON in this format:
    {{
    "SUMMARY": "...",
    "SKILLS": "...",
    "HOOPP_EXPERIENCE": "...",
    "PORTFOLIO_TRACKER": "...",
    "JOBPILOT": "..."
    }}
    """
    response = _call_llm_with_retries(prompt)
    if not response:
        print("⚠️ Falling back to original sections due to LLM failure.")
        return section_texts
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("⚠️ Model did not return valid JSON, raw output saved for debugging")
        return {}

# ---------- MAIN PIPELINE ----------
def add_text_with_bold(para, text):
    """
    Add text to a paragraph, bolding any content wrapped in **...**.
    """
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = para.add_run(part[2:-2])  # strip **
            run.bold = True
        else:
            para.add_run(part)
            
def insert_paragraph_after(paragraph, style=None):
    """Insert a new paragraph immediately after the given one."""
    new_para = paragraph._parent.add_paragraph("", style=style)  # create paragraph
    paragraph._element.addnext(new_para._element)  # insert directly after
    return new_para

def customize_resume_with_placeholders(template_path: str, section_files: dict, job_description: str, output_path: str, additional_info: str = None):
    """
    Replace placeholders in resume template with LLM-customized content.
    section_files = {"SUMMARY": "path/to/summary.txt", ...}
    """
    doc = Document(template_path)

    # Load all base texts
    section_texts = {}
    for placeholder, file_path in section_files.items():
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                section_texts[placeholder] = f.read()
        else:
            print(f"⚠️ Section file not found: {file_path}")

    # Clean job description
    cleaned_job_description = clean_job_description(job_description)

    # Get improved sections from LLM
    improved_sections = improve_resume_json(section_texts, cleaned_job_description, additional_info)
    # print the text of each section for debugging
    for section, text in improved_sections.items():
        print(f"--- {section} ---\n{text}\n")   
    if not improved_sections:
        print("❌ No improved sections returned, aborting placeholder replacement.")
        return

    # Build replacements dict ({{SUMMARY}} → improved text, etc.)
    replacements = {f"{{{{{k}}}}}": v for k, v in improved_sections.items()}

    # Replace in paragraphs and tables
    def replace_placeholders_in_doc(doc_obj, replacements: dict):
        for para in doc_obj.paragraphs:
            for key, value in replacements.items():
                if key in para.text:
                    section_name = key.strip("{}")   # e.g. "SUMMARY"
                    style = SECTION_STYLES.get(section_name, "Normal")

                    # split into lines (ignore empty lines)
                    items = [line.strip() for line in value.splitlines() if line.strip()]

                    # clear the placeholder paragraph
                    para.text = ""

                    # add first item
                    if items:
                        para.style = style
                        add_text_with_bold(para, items[0])

                        # insert the rest as new styled paragraphs (keep correct order)
                        current_para = para
                        for item in items[1:]:
                            new_para = insert_paragraph_after(current_para, style=style)
                            add_text_with_bold(new_para, item)
                            current_para = new_para  # advance pointer

        # Handle table placeholders too
        for table in doc_obj.tables:
            for row in table.rows:
                for cell in row.cells:
                    replace_placeholders_in_doc(cell, replacements)

    replace_placeholders_in_doc(doc, replacements)

    doc.save(output_path)
    print(f"✅ Customized resume saved to {output_path}")
 
