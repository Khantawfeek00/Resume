# ATS rules for this resume

Distilled from two Naukri Resume Analyser runs on `resume_calibri.pdf` (score moved Medium → High / top 23 %) plus general ATS behaviour. Rules marked **(observed)** fixed a real flag.

## Layout and LaTeX (keep as in master)

| Rule | Why |
|------|-----|
| `\usepackage[sfdefault,lining]{carlito}` | **(observed)** Default old-style numerals in Carlito have a broken Unicode map – phone, dates and every '5' extracted as '⁵⁰⁻⁰'. `lining` fixes it. |
| `\RaggedRight` (ragged2e) | **(observed)** Justified text squeezed spaces and the parser read `themwith`, `andMySQL`. Ragged-right never shrinks spaces. |
| `\hyphenpenalty=10000 \exhyphenpenalty=10000` | Hyphenated line breaks split keywords (`micro-\nservices`). |
| `\ifpdftex \input{glyphtounicode} \pdfgentounicode=1 \fi` | Correct ToUnicode under pdfLaTeX; the guard lets the same file compile under XeTeX/Tectonic. |
| Single column, no tables, no images, no text boxes, no headers/footers | Parsers read top-to-bottom; multi-column layouts scramble bullets. |
| US Letter, 10 pt body, margins ≥ 0.35 in | Analyser "right font size: 8–12 body" passed at 10 pt. |
| Exactly 1 page | Analyser "right number of pages" passed; recruiters expect 1 page at 3 years. |
| Section headings exactly: Summary, Skills, Work Experience, Projects, Education, Certifications | **(observed)** "Technical Skills" was reported as «Skills section missing». Parsers match literal heading names. |
| Compile with `tectonic` (installed) or pdfLaTeX; verify with `scripts/validate_resume.py` | Never deliver unverified. |

## Wording

| Rule | Why |
|------|-----|
| Every bullet starts with a strong past-tense action verb | **(observed)** Flag "use more action verbs". Approved: Designed, Developed, Built, Engineered, Architected, Implemented, Led, Executed, Delivered, Launched, Resolved, Achieved, Championed, Mentored, Optimised, Automated, Integrated, Migrated, Reduced, Improved, Owned, Directed, Managed, Planned, Established, Secured, Streamlined, Spearheaded. Avoid as openers: Partnered, Worked, Helped, Responsible, Assisted, Sustained, Adopted, Decoupled, Analyzed (weak/unrecognised). |
| No personal pronouns: I, me, my, we, our, them, their | **(observed)** "them" caused a flag. Rewrite ("integrated with X" → "integrated with X"). |
| No word repeated more than ~4 times (excluding stop words and core stack like Java/Spring) | **(observed)** "code" ×6 flagged; "Spring Security Spring Data JPA" flagged as a repeated phrase. Vary: code → review → peer reviews. |
| Only dictionary-spellable or bold lower-case product coinages | **(observed)** `pgvector` flagged ×3. Use "PostgreSQL vector store" or "Vector Database". Likewise prefer "MinIO" (accepted), "Keycloak" (accepted). |
| Bold 8–14 % of words: headings, titles, and key metrics only | **(observed)** Analyser asks for "up to 10 % bold"; too little is flagged, far more looks shouty. Bold numbers (35%, 85% coverage) not whole phrases. |
| 480–680 words | Analyser wants 250–500; below ~480 loses keywords, above ~680 forces 2 pages. Accept this flag rather than gut content. |
| Metrics in every bullet where truthful; keep the exact figures from facts.md | Recruiter scanning; analyser's own examples are metric-led. |
| Use the JD's spelling for each keyword (React.js vs ReactJS, Spring Boot vs SpringBoot, CI/CD vs CICD) | Many ATS do literal matching. Include both forms only if space allows (e.g. "REST APIs (RESTful)"). |
| Spell out acronyms once when the JD uses the long form (e.g. "Retrieval-Augmented Generation (RAG)") | Covers both match variants. |
| Dates as `Mon YYYY — Mon YYYY` with en-dash, "Present" for current | Parsers compute experience from these. |
| Contact line: City, Country \| email \| phone \| linkedin \| github – plain text, no icons | Icons become garbage glyphs. |

## Keyword placement priority

1. Header title line (highest weight in Naukri search and most ATS)
2. Summary first sentence
3. Skills section (literal match)
4. Experience bullets (context match – proves the skill was used)
5. Project tech-stack lines

A JD "required" keyword should appear in at least two of these places.

## Honesty guardrails

- Everything comes from `facts.md`. Reframing is allowed (Kafka → "event streaming (Apache Kafka)"); invention is not.
- If a JD requires something absent from facts.md, report it as a gap. Do not fabricate.
- Never change employer, client, titles, dates, metrics, phone, or email.

## Known checker quirks

- Naukri Resume Analyser detects the role from the header line ("Full Stack Developer role") – mirroring the JD title in the header aligns the benchmark.
- It treats "Technical Skills" as missing; "Skills" passes.
- It counts bold by characters; our validator approximates by words.
- Word-count flag (250–500) will remain at ~650 words; this is accepted.
