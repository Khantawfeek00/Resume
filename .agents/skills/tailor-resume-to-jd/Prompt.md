/tailor-resume-to-jd

Tailor my resume for the job description below.

Company: <COMPANY NAME>
Role: <ROLE TITLE AS WRITTEN IN THE JD>

Instructions:
1. Read .agents/skills/tailor-resume-to-jd/SKILL.md and follow its workflow end to end.
2. Save the JD below to jd/<company>-<role>.txt and run scripts/jd_keywords.py on it.
3. Use resume_calibri.tex as the master. Do NOT edit it. Create resume_<Company>_<Role>.tex and compile it with tectonic.
4. Use only claims from facts.md. Reframe wording to match the JD's exact spelling of each keyword, but never add a technology, metric, employer, title, or date that is not in facts.md. List anything the JD requires that I don't have as a gap — do not fabricate it.
5. Mirror the JD title in the header title line and the first sentence of the summary. Reorder Skills, bullets, and projects so JD keywords appear first.
6. Keep it to exactly one page. If content overflows, cut in the order given in SKILL.md.
7. Run scripts/validate_resume.py on the PDF with --jd and --png. Fix every FAIL and WARN, recompile, and re-run until it prints RESULT: PASS with REQUIRED keyword coverage ≥ 90%.
8. Show me the rendered page image.
9. Finish with a short report: files produced, validator summary line, keyword coverage with the exact missing terms split into "not in my experience" vs "left out for space", what changed in positioning, and the Naukri headline + key skills I should update to match.

Job description:
-----
<PASTE THE FULL JD HERE>
-----
