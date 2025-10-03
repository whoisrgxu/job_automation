# resume_customizer_tex.py
import os, re, json, subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import shutil

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-5-mini"    # or "gpt-5-mini"

SECTION_RULES = {
    "SUMMARY": """
    - Rewrite as 3–4 bullet points and make sure these bullets are coherent with one another.
    - Highlight the top 3–4 relevant technologies and 2–3 soft skills.
    - Keep professional, ATS-friendly tone.
    """,
    "SKILLS": """
    - Use 'Category: item1, item2' lines, no more than 5 categories.
    - Delete irrelevant skills.
    """,
     "HOOPP_EXPERIENCE": """
    - Max 6 bullets, <=150 words total.
    - Also produce a TAGS list of 6 short skill tokens (e.g., C#, .NET, CI/CD) relevant to JD and section content.
    """,
    "JOBPILOT": """
    - Max 4 bullets, <=105 words total.
    - Also produce a TAGS list of 6–9 most JD relevant short skill tokens.
    """,
    "PORTFOLIO_TRACKER": """
    - Max 4 bullets, <=130 words total.
    - Also produce a TAGS list of 6–9 most JD relevant short skill tokens.
    """,
}

def improve_resume_json(section_texts: dict, job_description: str, additional_info: str|None) -> dict:
    sections_str = "\n\n".join(f"{k}:\n{v}" for k, v in section_texts.items())
    rules_str = "\n".join(f"- {k}: {v.strip()}" for k, v in SECTION_RULES.items())
    prompt = f"""
You are a professional resume writer. Improve each section to better match the job.

General:

- treat the existing items as base and reframe if needed. Can delete irrelevant items.
- Emphasize JD alignment.
- Each bullet in any sections should not exceed 140 characters including spaces.
- You may integrate 2–4 additional skills from the job description that are not currently in the resume, but only if they fit naturally into the context of the section.
- Distribution of new skills is flexible:
* Some may appear in Hoopp Experience and Projects
* Some may overlap across sections if appropriate
* It is not required to use all missing skills
- Slight exaggeration of existing skills is acceptable, but do not fabricate unrelated skills.
- Do NOT prefix bullets or lines with '-', '*', '•', or numbers (just output plain text).
- Keep the tone professional and ATS-friendly.
- Output strictly valid JSON, no commentary.

Unique Rules:
{rules_str}

Job Description:
{job_description}

Sections:
{sections_str}

Additional Requirement:
{additional_info or 'None'}

Return JSON like:
{{
 "SUMMARY": "...",
 "SKILLS": "...",
 "HOOPP_EXPERIENCE": "...",
 "HOOPP_EXPERIENCE_TAGS": ["C#", ".NET", "CI/CD", "Azure DevOps", "Unit Testing", "Monitoring"],
 "PORTFOLIO_TRACKER": "...",
 "PORTFOLIO_TRACKER_TAGS": ["FastAPI", "PostgreSQL", "Docker", "Finnhub API", "Linux", "Git"],
 "JOBPILOT": "...",
 "JOBPILOT_TAGS": ["Next.js", "TypeScript", "MongoDB", "JWT", "OAuth2", "GitHub Actions"]
}}
"""
    r = client.chat.completions.create(model=MODEL, messages=[{"role":"user","content":prompt}])
    txt = r.choices[0].message.content.strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON from model.")
        return {}

# -------- LaTeX helpers --------
# def md_bold_to_tex(s: str) -> str:
#     return re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', s)
LATEX_ESC = [
    ('\\', r'\textbackslash{}'),
    ('#', r'\#'), ('$', r'\$'), ('%', r'\%'), ('&', r'\&'),
    ('_', r'\_'), ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}'),
    # no '{' or '}'
]

def escape_tex(s: str) -> str:
    out = s
    for a, b in LATEX_ESC:
        out = out.replace(a, b)
    return out

def normalize_bullet_lines(lines: list[str]) -> list[str]:
    """Ensure each bullet line ends with a period, unless it already ends with punctuation."""
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        # If it already ends with ., !, ?, or ; leave it as is
        if ln[-1] not in ".!?;":
            ln += "."
        out.append(ln)
    return out

def render_paragraph(s: str) -> str:
    s = escape_tex(s)
    paras = [p.strip() for p in s.split("\n\n") if p.strip()]
    return "\n\n".join(paras) + ("\n" if paras else "")

def render_bullets(s: str) -> str:
    s = escape_tex(s)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    lines = normalize_bullet_lines(lines)  # ✅ enforce punctuation
    if not lines:
        return ""
    items = "\n".join(f"  \\item {ln}" for ln in lines)
    return "\\begin{itemize}\n" + items + "\n\\end{itemize}\n"

def render_skill_block(skills_text: str) -> str:
    lines = [ln for ln in (ln.strip() for ln in skills_text.splitlines()) if ln]
    out = []
    for ln in lines:
        ln = re.sub(r"^[-*•\d]+[.)]?\s+", "", ln)
        if ":" in ln:
            cat, items = ln.split(":", 1)
            cat_tex   = escape_tex(cat.strip())
            items_tex = escape_tex(items.strip())
            out.append(rf"  \item \textbf{{{cat_tex}}}: {items_tex}")
        else:
            out.append(rf"  \item {escape_tex(ln)}")

    if not out:
        return ""
    return r"\begin{itemize}[]" + "\n" + "\n".join(out) + "\n" + r"\end{itemize}" + "\n"

def render_tags_inline(tags: list[str]) -> str:
    r"""Emit inline \cvtag{\textbf{...}} \cvtag{\textbf{...}} with no line breaks."""
    if not tags:
        return ""
    cleaned = []
    for t in tags:
        if not t:
            continue
        t = re.sub(r"^[-*•\d]+[.)]?\s+", "", t.strip())  # strip accidental prefixes
        cleaned.append(escape_tex(t))
    # join with a single space, no trailing newline
    return " ".join(rf"\cvtag{{\textbf{{{t}}}}}" for t in cleaned)

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_sources(section_files: dict) -> dict:
    out = {}
    for k, p in section_files.items():
        out[k] = Path(p).read_text(encoding="utf-8") if p and Path(p).exists() else ""
    return out

def latexmk_xelatex(main_tex: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    cwd = main_tex.parent  # <- run from the template folder

    latexmk = shutil.which("latexmk")
    xelatex = shutil.which("xelatex")

    if latexmk:
        # -cd: change into the directory containing the main file
        cmd = [
            latexmk, "-cd", "-xelatex", "-interaction=nonstopmode",
            f"-outdir={str(outdir)}", "resume.tex"  # pass relative name
        ]
        proc = subprocess.run(cmd, cwd=str(cwd))
        if proc.returncode == 0:
            return
        print("⚠️ latexmk failed; falling back to xelatex…")

    if xelatex:
        # Run XeLaTeX twice; still run from source folder
        cmd = [xelatex, "-interaction=nonstopmode",
               "-output-directory", str(outdir), "resume.tex"]
        subprocess.run(cmd, cwd=str(cwd))
        subprocess.run(cmd, cwd=str(cwd))
    else:
        print("⚠️ Neither latexmk nor xelatex found. Skipping compile.")

def customize_resume_sections_tex(
    template_folder: Path,
    section_files: dict,
    job_description: str,
    additional_info: str|None = None,
    compile_pdf: bool = True,
    final_pdf_name: str = "resume.pdf"
):
    """
    Writes LaTeX partials into <template_folder>/sections/*.tex,
    then optionally builds the PDF.
    """
    # 1) load sources or LLM-improved text
    base = load_sources(section_files)
    improved = improve_resume_json(base, job_description, additional_info) or base

    # 2) decide render mode per section
    #    (bullets for experience/projects; paragraphs for summary/skills)
    out_sections = template_folder / "sections"
    write(out_sections / "summary_items.tex", render_bullets(improved.get("SUMMARY","")))
    write(out_sections / "skill_items.tex",
        render_skill_block(improved.get("SKILLS", "")))
    write(out_sections / "hoopp_experience.tex",  render_bullets  (improved.get("HOOPP_EXPERIENCE","")))
    write(out_sections / "portfolio_tracker.tex", render_bullets  (improved.get("PORTFOLIO_TRACKER","")))
    write(out_sections / "jobpilot.tex",          render_bullets  (improved.get("JOBPILOT","")))

    # tags (new)
    write(out_sections / "jobpilot_tags.tex",
        render_tags_inline(improved.get("JOBPILOT_TAGS", [])))
    write(out_sections / "portfolio_tags.tex",
        render_tags_inline(improved.get("PORTFOLIO_TRACKER_TAGS", [])))
    write(out_sections / "hoopp_tags.tex",
        render_tags_inline(improved.get("HOOPP_EXPERIENCE_TAGS", [])))

    print(f"✅ Wrote LaTeX snippets to {out_sections}")

    # 3) compile
    if compile_pdf:

        main  = template_folder / "resume.tex"
        build = template_folder / "build"
        latexmk_xelatex(main, build)
        pdf_out = build / "resume.pdf"

        if pdf_out.exists():
            final = template_folder / final_pdf_name
            shutil.copy2(pdf_out, final)
            print(f"✅ Built PDF: {final}")
        else:
            print("⚠️ PDF not found. Check LaTeX logs in build/.")
