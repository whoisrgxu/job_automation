import os
from docx import Document
from LLMClients.clients import Model

# === Step 1: find resume ending with "Resume.docx" ===
def get_resume_from_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith("Resume.docx"):
            return os.path.join(folder_path, file)
    raise FileNotFoundError("No resume file ending with 'Resume.docx' found.")

# === Step 2: get cover letter template path ===
cover_letter_path_file = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/cover_letter_path.txt"
with open(cover_letter_path_file, "r") as f:
    cover_letter_template_path = f.read().strip()

resume_folder = os.path.dirname(cover_letter_template_path)
resume_path = get_resume_from_folder(resume_folder)

# === Step 3: read job description ===
jd_path = os.path.join(os.path.dirname(cover_letter_template_path), "job_description.txt")
with open(jd_path, "r") as f:
    job_description = f.read()

# === Step 4: prepare prompt ===
with open(resume_path, "rb") as f:
    resume_doc = Document(f)
    resume_text = "\n".join([p.text for p in resume_doc.paragraphs])

prompt = f"""
You are an assistant that writes professional job application cover letters.
Use the resume and job description below to generate only the **body text**
of the cover letter (no greeting like "Hi Hiring Team" and no ending with my name).
Should be confident and professional, and a bit natural, but not using "—" or "'", and not too much focus on the things repetitively mentioned in resume, i meant not too much detail and no less than 250 and no more than 300 words.

Resume:
{resume_text}

Job Description:
{job_description}
"""

llm = Model("GEMINI", prompt)

# # response = client.chat.completions.create(
# #     model="gpt-5-mini",   # you can adjust model
# #     messages=[{"role": "user", "content": prompt}],
# # )
# response = client.models.generate_content(
#     model="gemini-2.5-pro", contents=prompt
# )

# # cover_letter_body = response.choices[0].message.content.strip()
# cover_letter_body = response.candidates[0].content.parts[0].text
cover_letter_body = llm.get_response_from_client()

# === Step 5: insert into template ===
doc = Document(cover_letter_template_path)

for para in doc.paragraphs:
    if "{{COVER_LETTER_BODY}}" in para.text:
        para.text = cover_letter_body
        para.style = "NewCoverLetterStyle"  # Apply your custom style
        break

output_path = cover_letter_template_path.replace("_Template.docx", ".docx")
doc.save(output_path)

print(f"✅ Cover letter generated: {output_path}")
