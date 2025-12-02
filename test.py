import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from docx import Document
from openpyxl import Workbook, load_workbook

from resume_customizer import customize_resume_with_placeholders

import subprocess

excel_log_path = "/Users/Roger/Documents/FullTime-Resume/Job Tracker.xlsx"


def convert_docx_to_pdf(docx_path: str) -> str:
    """
    Convert a DOCX file to PDF in the same folder.
    Tries methods in order: WPS Office (via AppleScript), LibreOffice.
    Returns the path to the PDF file if successful, None otherwise.
    This function will NEVER raise exceptions - all errors are caught and logged.
    """
    try:
        docx_path_obj = Path(docx_path)
        if not docx_path_obj.exists():
            print(f"⚠️ DOCX file not found: {docx_path}")
            return None
        
        # Output PDF path (same folder, same name, .pdf extension)
        pdf_path = docx_path_obj.with_suffix('.pdf')
        output_dir = docx_path_obj.parent
        docx_abs_path = str(docx_path_obj.resolve())
        pdf_filename = pdf_path.name
        
        # Method 1: Try WPS Office (user's preferred office suite) via AppleScript
        wps_app_paths = [
            "/Applications/WPS Office.app",
            "/Applications/Kingsoft Office.app",
        ]
        
        wps_found = False
        for wps_app in wps_app_paths:
            if Path(wps_app).exists():
                wps_found = True
                print(f"📝 Attempting PDF conversion with WPS Office...")
                try:
                    # AppleScript to automate WPS Office to export to PDF
                    # Note: WPS Office menu structure may vary - this is a simplified approach
                    applescript = f'''
                    tell application "WPS Office"
                        activate
                        open POSIX file "{docx_abs_path}"
                    end tell
                    delay 4
                    tell application "System Events"
                        tell process "WPS Office"
                            try
                                -- Try keyboard shortcut for export/save as PDF (Cmd+Shift+E or Cmd+P then export)
                                -- First, try Save As dialog approach
                                keystroke "s" using {{command down, shift down}}
                                delay 2
                                -- In Save As dialog, set format to PDF if possible
                                -- This is a simplified approach - actual menu may differ
                                keystroke return
                                delay 2
                            on error errMsg
                                return "Error: " & errMsg
                            end try
                        end tell
                    end tell
                    delay 3
                    tell application "WPS Office"
                        quit
                    end tell
                    '''
                    
                    result = subprocess.run(
                        ["osascript", "-e", applescript],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    # Check if PDF was created (might have a different name if Save As was used)
                    # Look for any PDF file with similar name in the output directory
                    if pdf_path.exists():
                        print(f"✅ PDF exported using WPS Office: {pdf_path}")
                        return str(pdf_path)
                    
                    # Also check if any PDF was created in the directory
                    pdf_files = list(output_dir.glob("*.pdf"))
                    if pdf_files:
                        # Find the most recent PDF that might match
                        recent_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
                        if recent_pdf.stat().st_mtime > docx_path_obj.stat().st_mtime:
                            print(f"⚠️ WPS Office created PDF but with different name: {recent_pdf}")
                            # Rename to expected name
                            recent_pdf.rename(pdf_path)
                            print(f"✅ PDF exported using WPS Office: {pdf_path}")
                            return str(pdf_path)
                    
                    print(f"⚠️ WPS Office automation attempted but PDF not created")
                    if result.stderr:
                        print(f"   Error: {result.stderr}")
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                    print(f"⚠️ WPS Office conversion failed: {e}")
                break
        
        # Method 2: Try LibreOffice (most reliable command-line method)
        if not wps_found or not pdf_path.exists():
            libreoffice_paths = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            "/usr/local/bin/soffice",
            "/opt/homebrew/bin/soffice",
            shutil.which("soffice"),
        ]
        
        libreoffice_cmd = None
        for path in libreoffice_paths:
            if path and Path(path).exists():
                libreoffice_cmd = path
                break
        
        if libreoffice_cmd:
            print(f"📝 Attempting PDF conversion with LibreOffice...")
            try:
                # LibreOffice command to convert to PDF
                cmd = [
                    libreoffice_cmd,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(output_dir),
                    str(docx_path_obj)
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0 and pdf_path.exists():
                    print(f"✅ PDF exported using LibreOffice: {pdf_path}")
                    return str(pdf_path)
                elif result.stderr:
                    print(f"⚠️ LibreOffice conversion failed: {result.stderr[:200]}")
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                print(f"⚠️ LibreOffice conversion failed: {e}")
        
        # All methods failed - log warning but don't fail the script
        if not pdf_path.exists():
            if wps_found:
                print(f"⚠️ PDF conversion unsuccessful. WPS Office automation needs improvement.")
                print(f"💡 The DOCX files are available for manual PDF export.")
                print(f"   Or install LibreOffice for reliable command-line PDF conversion: brew install --cask libreoffice")
            else:
                print(f"⚠️ PDF conversion skipped: No compatible office suite found.")
                print(f"💡 Tip: Install LibreOffice for reliable command-line PDF conversion: brew install --cask libreoffice")
        
        # Return None gracefully - this is not a critical error
        return None
    
    except Exception as e:
        # Catch ANY unexpected exception to prevent script from crashing
        print(f"⚠️ Unexpected error in PDF conversion (non-critical): {e}")
        print(f"   DOCX file is still available: {docx_path}")
        return None


def log_application_to_excel(excel_path, sheet_name, company_name, position_name, applied_date, job_description=None):
    if os.path.exists(excel_path):
        wb = load_workbook(excel_path)
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        else:
            ws = wb.create_sheet(sheet_name)
            ws.append(["Company", "Position", "Applied Date", "Job Description"])
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        ws.append(["Company", "Position", "Applied Date", "Job Description"])

    # Append
    ws.append([company_name, position_name, applied_date, job_description or ""])
    print(f"➡️ Logging row: {company_name}, {position_name}, {applied_date}")  # debug

    wb.save(excel_path)
    print(f"💾 Saved to {excel_path}")


def replace_placeholders_in_docx(input_path, output_path, replacements: dict):
    """Replace placeholders like {{COMPANY_NAME}} in a Word document."""
    doc = Document(input_path)
    for para in doc.paragraphs:
        for key, value in replacements.items():
            if key in para.text:
                for run in para.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)
    doc.save(output_path)


def create_application_folder(company_name, position_name, position_type, resume_path, coverLetter_path, jd_source_path=None):
    """
    Create an application folder for a company/position, copy resume & cover letter,
    copy job description file, and optionally customize resume with LLM.
    """
    parent_folder = os.path.dirname(resume_path)
    grandparent_folder = os.path.dirname(parent_folder)

    # Create folders
    company_folder = os.path.join(grandparent_folder, company_name)
    os.makedirs(company_folder, exist_ok=True)
    position_folder = os.path.join(company_folder, position_name)
    os.makedirs(position_folder, exist_ok=True)

    # Define filenames
    resume_filename = f"Roger Xu_{company_name}_Resume_Template.docx"
    cover_filename = f"Roger Xu_{company_name}_CoverLetter_Template.docx"
    jd_filename = "job_description.txt"

    resume_target = os.path.join(position_folder, resume_filename)
    cover_target = os.path.join(position_folder, cover_filename)
    jd_target = os.path.join(position_folder, jd_filename)

    # Date string
    today_str = datetime.today().strftime("%B %d, %Y")

    # Placeholder replacements
    replacements = {
        "{{COMPANY_NAME}}": company_name,
        "{{POSITION_NAME}}": position_name,
        "{{TODAY_DATE}}": today_str
    }

    # Step 1: Copy resume template
    shutil.copy(resume_path, resume_target)

    # Step 2: Copy JD and read additional_info if present
    job_description = None
    additional_info = None

    if jd_source_path and os.path.exists(jd_source_path):
        shutil.copy(jd_source_path, jd_target)
        with open(jd_target, "r") as f:
            job_description = f.read()

        addl_source_path = os.path.join(os.path.dirname(jd_source_path), "additional_info.txt")
        if os.path.exists(addl_source_path):
            with open(addl_source_path, "r") as f:
                additional_info = f.read()
            print("ℹ️ Loaded additional_info.txt")

    # Step 3: Customize resume
    # position type folder name such as Frontend_Sections or Frontend_Sections
    position_type_folder_name = position_type.capitalize() + "_Sections"
    if job_description:
        section_files = {
            "SUMMARY": f"/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/{position_type_folder_name}/summary.txt",
            "HOOPP_EXPERIENCE": f"/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/{position_type_folder_name}/hoopp_experience.txt",
            "PORTFOLIO_TRACKER": f"/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/{position_type_folder_name}/portfolio_tracker.txt",
            "SKILLS": f"/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/{position_type_folder_name}/skills.txt",
            "JOBPILOT": f"/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/{position_type_folder_name}/jobpilot.txt",
        }

        customized_resume_path = os.path.join(
            position_folder,
            f"Roger Xu_{company_name}_Resume.docx"
        )
        customize_resume_with_placeholders(
            resume_path,
            section_files,
            job_description,
            customized_resume_path,
            additional_info
        )
        resume_target = customized_resume_path
        
        # Export resume as PDF
        print("📄 Exporting resume to PDF...")
        try:
            convert_docx_to_pdf(customized_resume_path)
        except Exception as e:
            print(f"⚠️ PDF export failed (non-critical): {e}")
            print("   Resume DOCX file is still available for manual PDF export.")

    # Step 4: Generate cover letter
    replace_placeholders_in_docx(coverLetter_path, cover_target, replacements)

    print(f"✅ Application folder created: {position_folder}")
    print(f"📄 Files created:\n- {resume_target}\n- {cover_target}\n- {jd_target}")

    log_application_to_excel(
        excel_log_path,
        sheet_name="Job Tracker",
        company_name=company_name,
        position_name=position_name,
        applied_date=today_str,
        job_description=job_description,
    )
    print(f"📝 Logged application to {excel_log_path}")
    
    # Step 5: Clear only the source job_description.txt and additional_info.txt
    try:
        # Clear the original JD file (template folder)
        if jd_source_path and os.path.exists(jd_source_path):
            open(jd_source_path, "w").close()
            print("🧹 Cleared source job_description.txt content")

        # Clear additional_info.txt if present in source folder
        addl_source_path = os.path.join(os.path.dirname(jd_source_path), "additional_info.txt")
        if os.path.exists(addl_source_path):
            open(addl_source_path, "w").close()
            print("🧹 Cleared source additional_info.txt content")
    except Exception as e:
        print(f"⚠️ Failed to clear source job description/additional_info: {e}")

    # --- NEW: record cover letter absolute path ---
    try:
        record_cover_path = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/cover_letter_path.txt"
        with open(record_cover_path, "w") as f:
            f.write(cover_target)
        print(f"📝 Recorded cover letter path: {cover_target} → {record_cover_path}")
    except Exception as e:
        print(f"⚠️ Failed to write cover letter path: {e}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py <CompanyName> <PositionName> <Type>")
        sys.exit(1)

    # Resume templates
    resume_default = "/Users/Roger/Documents/FullTime-Resume/Rong Gang Xu_Resume_v3.docx"
    resume_frontend = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Frontend_Resume_Placeholder.docx"
    resume_fullstack = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Fullstack_Resume_Placeholder.docx"
    resume_sharepoint = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_SharePoint_Resume.docx"
    coverLetter = "/Users/Roger/Documents/FullTime-Resume/Roger Xu_coverletter.docx"

    jd_source_path = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/job_description.txt"

    # CLI args
    company = sys.argv[1].strip()
    position = sys.argv[2].strip()
    position_type = sys.argv[3]
    
    # easy_apply default is true
    if len(sys.argv) < 5:
        easy_apply = "true"
    else:
        easy_apply = sys.argv[4].strip().lower()

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

    folder_created = create_application_folder(company, position, position_type, resume, coverLetter, jd_source_path)

    # Reconstruct the cover letter path
    parent_folder = os.path.dirname(resume)
    grandparent_folder = os.path.dirname(parent_folder)
    company_folder = os.path.join(grandparent_folder, company)
    position_folder = os.path.join(company_folder, position)
    cover_filename = f"Roger Xu_{company}_CoverLetter_Template.docx"
    cover_target = os.path.join(position_folder, cover_filename)

    # If not easy apply, run coverletter customizer
    if easy_apply == "false" and folder_created:
        print("🔄 Running coverletter customizer...")
        import subprocess
        coverletter_script = "/Users/Roger/Documents/PersonalProject/Job Automation/coverletter_customizer.py"
        try:
            subprocess.run(f"python3 \"{coverletter_script}\"", shell=True, check=True)
            print("✅ Cover letter customized successfully")
            
            # Export cover letter as PDF (after customization)
            # The coverletter_customizer.py saves the customized cover letter,
            # which replaces "_Template.docx" with ".docx"
            print("📄 Exporting cover letter to PDF...")
            try:
                customized_cover_path = cover_target.replace("_Template.docx", ".docx")
                if os.path.exists(customized_cover_path):
                    convert_docx_to_pdf(customized_cover_path)
                else:
                    # Fallback to template version if customized version doesn't exist
                    convert_docx_to_pdf(cover_target)
            except Exception as e:
                print(f"⚠️ PDF export failed (non-critical): {e}")
                print("   Cover letter DOCX file is still available for manual PDF export.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to customize cover letter: {e}")
    elif folder_created:
        # Export cover letter as PDF even if not customized (for easy_apply cases)
        print("📄 Exporting cover letter to PDF...")
        try:
            convert_docx_to_pdf(cover_target)
        except Exception as e:
            print(f"⚠️ PDF export failed (non-critical): {e}")
            print("   Cover letter DOCX file is still available for manual PDF export.")