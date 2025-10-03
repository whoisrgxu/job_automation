import os
import shutil
import sys
from docx import Document
from datetime import datetime


def replace_placeholders_in_docx(input_path, output_path, replacements: dict):
    doc = Document(input_path)
    for para in doc.paragraphs:
        for key, value in replacements.items():
            if key in para.text:
                for run in para.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)
    doc.save(output_path)


def create_application_folder(company_name, position_name, resume_path, coverLetter_path):
    # Get the folder where resume is stored
    parent_folder = os.path.dirname(resume_path)

    # Create company and position subfolders
    grandparent_folder = os.path.dirname(parent_folder)
    company_folder = os.path.join(grandparent_folder, company_name)
    os.makedirs(company_folder, exist_ok=True)

    position_folder = os.path.join(company_folder, position_name)
    os.makedirs(position_folder, exist_ok=True)

    # Define new filenames
    resume_filename = f"Roger Xu_{company_name}_Resume.docx"
    cover_filename = f"Roger Xu_{company_name}_CoverLetter.docx"

    # Copy and rename the files
    resume_target = os.path.join(position_folder, resume_filename)
    cover_target = os.path.join(position_folder, cover_filename)

    # Date string (e.g., "May 21, 2025")
    today_str = datetime.today().strftime("%B %d, %Y")

    # Replacements
    replacements = {
        "{{COMPANY_NAME}}": company_name,
        "{{POSITION_NAME}}": position_name,
        "{{TODAY_DATE}}": today_str
    }
    #copy the resume_file to the new location
    shutil.copy(resume_path, resume_target)
    # Replace in resume and cover letter
    replace_placeholders_in_docx(coverLetter_path, cover_target, replacements)

    print(f"Application folder created: {position_folder}")
    print(f"Files created and customized:\n- {resume_target}\n- {cover_target}")



if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <CompanyName> <PositionName><type>")
        sys.exit(1)

    # Replace these with your actual Word file paths
    resume_default = "/Users/Roger/Documents/FullTime-Resume/Rong Gang Xu_Resume_v3.docx"
    resume_frontend = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Frontend_Resume.docx"
    resume_fullstack = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Fullstack_Resume.docx"
    resume_sharepoint = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_SharePoint_Resume.docx"
    coverLetter = "/Users/Roger/Documents/FullTime-Resume/Roger Xu_coverletter.docx"

    company = sys.argv[1]
    position = sys.argv[2]
    position_type = sys.argv[3]
    if position_type == "default":
        resume = resume_default
    elif position_type == "frontend":
        resume = resume_frontend
    elif position_type == "fullstack":
        resume = resume_fullstack
    elif position_type == "sharepoint":
        resume = resume_sharepoint
    else:
        print("Invalid position type. Use 'default', 'frontend', 'fullstack', or 'sharepoint'.")
        sys.exit(1)
    create_application_folder(company, position, resume, coverLetter)
