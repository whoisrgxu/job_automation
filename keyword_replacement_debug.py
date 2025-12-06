from docx import Document

doc = Document("/Users/Roger/Documents/FullTime-Resume/Roger Xu_coverletter.docx")

for i, para in enumerate(doc.paragraphs):
    if "LOCATION_STRING" in para.text:
        print(f"Paragraph {i}: {para.text!r}")
        for j, run in enumerate(para.runs):
            print(f"  run {j}: {run.text!r}")