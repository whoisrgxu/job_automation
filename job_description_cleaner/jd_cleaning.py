from LLMClients.clients import Model

def clean_job_description(job_description):
    """
    Clean job description using LLM to remove fluff and keep only relevant technical information.
    """
    prompt = f"""You are a professional job data cleaner for an automated resume-matching system.

Your goal is to clean the following job description by keeping only the core technical and role-relevant information.

Please remove:

- Marketing or HR fluff (e.g., "Why Join Us", "About the Company", "Our Culture", "Perks", "Benefits", "What's in it for you").
- Repeated or generic motivational text.
- Unrelated sections like diversity statements, salary ranges, equal opportunity policies, or application instructions.

Please keep:

- Job title (if mentioned in context)
- Responsibilities and daily tasks
- Required skills, tools, and technologies
- Education or experience requirements
- Key qualifications that determine technical fit

Output the cleaned text in plain format, with no commentary, markdown, or extra formatting.

The goal is to make the text concise and focused for an LLM-based resume-to-job fit analysis system.

JOB DESCRIPTION TO CLEAN:
{job_description}"""

    # Use the LLMClients class to get cleaned job description
    llm = Model("GEMINI", prompt)
    print(f"Cleaning job description...")
    try:    
        cleaned_description = llm.get_response_from_client()
    except Exception as e:
        print(f"Error cleaning job description: {e}")
        return job_description.strip()
    print(f"Job description cleaned successfully")
    return cleaned_description.strip()