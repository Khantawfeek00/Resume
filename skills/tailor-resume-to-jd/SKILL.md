---
name: tailor-resume-to-jd
description: Tailor Tawfeek Khan's LaTeX resume (resume_calibri.tex) to a specific job description and compile an ATS-optimised one-page PDF. Use when the user pastes or attaches a JD, says "tailor/optimise/update my resume for this job/role/company", asks for an ATS-friendly resume, or wants a resume for a specific application. Produces a new tailored .tex + .pdf, validates ATS score (keyword coverage, one page, text extraction, grammar rules) with scripts/validate_resume.py, and never invents experience not listed in facts.md.
---

# Tailor Resume to JD

Goal: a one-page PDF that scores 95%+ on ATS checkers (Naukri Resume Analyser, Jobscan-style keyword match) and reads well to a human recruiter, while staying 100% truthful.

## Inputs

- **Master resume**: `resume_calibri.tex` in the workspace root. Never edit it directly; copy it.
- **Ground truth**: [facts.md](facts.md) – everything that may be claimed. Nothing outside it goes on the resume.
- **ATS rules**: [ats-rules.md](ats-rules.md) – formatting and wording rules learned from real analyser runs. Read before writing.
- **JD**: pasted text, attached file, or URL. If only a URL is given, fetch it; if fetching fails, ask the user to paste the text.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Save JD to jd/<company>-<role>.txt
- [ ] 2. Extract JD keywords: python3 scripts/jd_keywords.py jd/<file>.txt
- [ ] 3. Map keywords -> facts.md (have / can-reframe / do-not-have)
- [ ] 4. Copy master -> resume_<Company>_<Role>.tex and rewrite
- [ ] 5. Compile: tectonic resume_<Company>_<Role>.tex
- [ ] 6. Validate: python3 scripts/validate_resume.py resume_<Company>_<Role>.pdf --jd jd/<file>.txt
- [ ] 7. Fix every FAIL/WARN, recompile, re-validate until PASS
- [ ] 8. Visual check (render page to PNG and inspect)
- [ ] 9. Report: keyword coverage, gaps the user cannot honestly close, files produced
```

### Step 1–2: JD keywords

`scripts/jd_keywords.py` prints JD keywords grouped as **required / preferred / soft**, with frequency, plus the JD's exact job title and seniority. Use the JD's own spelling for every term (e.g. "ReactJS" vs "React.js", "Spring Boot" vs "SpringBoot") – ATS matching is often literal.

### Step 3: Map to facts

For each JD keyword decide:

| Bucket | Rule |
|--------|------|
| **Have** | Appears in facts.md → must appear on the resume, ideally in Skills *and* in a bullet. |
| **Can reframe** | Facts cover it under another name (e.g. JD says "event streaming", facts say Kafka) → use the JD's term alongside the fact's term. |
| **Do not have** | Not in facts.md → do **not** add. List it in the final report as a gap. |

Never add a technology, metric, employer, title, or date that is not in facts.md. If the user says "just add X", add it only after they confirm they have actually used X, then append it to facts.md as well.

### Step 4: Rewrite the copy

Edit only content; keep the preamble, fonts, margins, and section order from the master unless a rule in ats-rules.md says otherwise.

1. **Header title line** – mirror the JD title: `<JD title> | <4–6 top JD keywords>`. If the JD title is "Java Full Stack Developer", the line starts with that, not "Senior Software Engineer".
2. **Summary** (4–5 lines) – first sentence contains the JD title and years of experience; include the top 6–8 JD keywords naturally; end with certifications relevant to the JD.
3. **Skills** – section heading must be exactly `Skills`. Reorder categories so JD-critical ones come first; put JD keywords first within each line; remove skills the JD does not care about if space is needed.
4. **Work Experience bullets** – reorder so bullets matching the JD come first; swap in JD terminology; keep every metric. Each bullet starts with a strong action verb (see ats-rules.md list). Max 9 bullets for the current role, 1 for the internship.
5. **Projects** – lead with the project most relevant to the JD. If the JD is pure backend, the AI Document Management System still stays (GenAI is a differentiator) but its bullets emphasise microservices/Kafka over React. Drop the Airbnb project if space is needed.
6. **Education / Certifications** – unchanged, except drop a certification only if the JD makes it irrelevant and space is critical.

### Step 5–7: Compile and validate

```bash
tectonic resume_<Company>_<Role>.tex
python3 scripts/validate_resume.py resume_<Company>_<Role>.pdf --jd jd/<company>-<role>.txt
```

`validate_resume.py` requires `pymupdf` (`pip install pymupdf`). It checks:

- exactly 1 page; 480–680 words
- digits and spaces extract correctly (no `themwith`, no garbage glyphs)
- no hyphenated line breaks
- all six section headings present with ATS-standard names
- every bullet starts with an approved action verb; no personal pronouns
- bold ratio 8–14 % of words
- no word repeated > 4 times (excluding stop words and the candidate's core stack)
- **JD keyword coverage** – prints matched / missing; target ≥ 90 % of *required* and ≥ 75 % overall

Iterate until the script prints `RESULT: PASS`. Do not hand over a resume with a FAIL.

### Step 8: Visual check

Render page 1 (`python3 scripts/validate_resume.py <pdf> --png /tmp/p1.png`) and read the image. Look for: orphaned single words on a line, uneven bottom whitespace (> 1.5 cm means room to restore a dropped bullet), and header links intact.

### Step 9: Report

Tell the user, in this order:

1. Files produced (`.tex`, `.pdf`) and the validator summary line.
2. JD keyword coverage and the exact missing terms, split into "not in your experience" vs "left out for space".
3. Anything changed in positioning (title line, which project leads).
4. Reminder: update the Naukri headline / key skills to the same JD terms before applying (see `Naukri_Profile_Final.md`).

## Non-negotiables

- One page. If content overflows, cut in this order: Airbnb project → least-relevant experience bullet → skill tokens the JD does not mention → shorten summary. Never shrink font below 10 pt or margins below 0.35 in.
- Truthful: facts.md is the only source. Phone, email, dates, employer, client, metrics stay exactly as in facts.md.
- Keep `\usepackage[sfdefault,lining]{carlito}`, `\RaggedRight`, `\hyphenpenalty=10000`, and the `\ifpdftex` guard – they fix real ATS extraction bugs (see ats-rules.md).
- Section headings exactly: `Summary`, `Skills`, `Work Experience`, `Projects`, `Education`, `Certifications`.
