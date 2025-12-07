import os
import subprocess
import sys

from application_helpers import convert_docx_to_pdf, create_application_folder


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <CompanyName> <PositionName> [easy_apply] [location] [job_category]")
        sys.exit(1)

    # Resume templates
    resume_default = "/Users/Roger/Documents/FullTime-Resume/Rong Gang Xu_Resume_v3.docx"
    resume_frontend = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Frontend_Resume_Placeholder.docx"
    resume_sde = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Fullstack_Resume_Placeholder.docx"
    resume_application_support = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Application_Support_Resume_Placeholder.docx"
    resume_cloud_support = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_Cloud_Support_Resume_Placeholder.docx"
    resume_sharepoint_support = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_SharePoint_Support_Resume_Placeholder.docx" 
    resume_sharepoint = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/Roger Xu_SharePoint_Resume.docx"
    coverLetter = "/Users/Roger/Documents/FullTime-Resume/Roger Xu_coverletter.docx"

    jd_source_path = "/Users/Roger/Documents/FullTime-Resume/Resume Template - One Page/job_description.txt"

    # CLI args
    company = sys.argv[1].strip()
    position = sys.argv[2].strip()

    # Optional args with safe defaults
    easy_apply = sys.argv[3].strip().lower() if len(sys.argv) > 3 else "true"
    location = sys.argv[4].strip() if len(sys.argv) > 4 else "Toronto, ON"
    job_category = sys.argv[5].strip().lower() if len(sys.argv) > 5 else "sde"

    print("======== DEBUG ARGS ========")
    print("sys.argv:", sys.argv)
    print("company:", company)
    print("position:", position)
    print("easy_apply:", easy_apply)
    print("location:", location)
    print("job_category:", job_category)
    print("============================")

    # Select resume template based on position_type
    if job_category == "sde":
        resume = resume_sde
    elif job_category == "application_support":
        resume = resume_cloud_support
    elif job_category == "cloud_support":
        resume = resume_cloud_support
    else:
        resume = resume_sharepoint_support  # fallback

    print(f"[DEBUG main] Using resume template: {resume!r}")

    # Create folder & base files
    folder_created = create_application_folder(
        company,
        position,
        resume,
        coverLetter,
        location,
        jd_source_path,
        job_category=job_category,
    )

    # Reconstruct the cover letter path (same logic as inside create_application_folder)
    parent_folder = os.path.dirname(resume)
    grandparent_folder = os.path.dirname(parent_folder)
    company_folder = os.path.join(grandparent_folder, company)
    position_folder = os.path.join(company_folder, position)
    cover_filename = f"Roger Xu_{company}_CoverLetter_Template.docx"
    cover_target = os.path.join(position_folder, cover_filename)

    # If not easy apply, run coverletter customizer
    if easy_apply == "false" and folder_created:
        print("🔄 Running coverletter customizer...")
        coverletter_script = "/Users/Roger/Documents/PersonalProject/Job Automation/coverletter_customizer.py"
        try:
            subprocess.run(f"python3 \"{coverletter_script}\"", shell=True, check=True)
            print("✅ Cover letter customized successfully")

            # Export cover letter as PDF (after customization)
            print("📄 Exporting cover letter to PDF...")
            try:
                customized_cover_path = cover_target.replace("_Template.docx", ".docx")
                if os.path.exists(customized_cover_path):
                    convert_docx_to_pdf(customized_cover_path)
                else:
                    convert_docx_to_pdf(cover_target)
            except Exception as e:
                print(f"⚠️ PDF export failed (non-critical): {e}")
                print("   Cover letter DOCX file is still available for manual PDF export.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to customize cover letter: {e}")
    elif folder_created:
        # Easy apply: still export cover letter as PDF (template-based)
        print("📄 Exporting cover letter to PDF (easy apply)...")
        try:
            convert_docx_to_pdf(cover_target)
        except Exception as e:
            print(f"⚠️ PDF export failed (non-critical): {e}")
            print("   Cover letter DOCX file is still available for manual PDF export.")
