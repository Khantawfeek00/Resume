#!/usr/bin/env python3
"""Validate a compiled resume PDF against ATS rules and (optionally) a JD.

Usage:
    python3 validate_resume.py resume.pdf
    python3 validate_resume.py resume.pdf --jd jd/company-role.txt
    python3 validate_resume.py resume.pdf --png /tmp/p1.png      # also render page 1

Requires: pip install pymupdf
Exit code 0 on PASS, 1 on FAIL. WARNs do not fail but should be reviewed.
"""
import os
import re
import subprocess
import sys

try:
    import pymupdf as fitz  # PyMuPDF >= 1.24
except ImportError:  # older name
    try:
        import fitz  # type: ignore
    except ImportError:
        sys.exit("pymupdf missing: pip install pymupdf")

HERE = os.path.dirname(os.path.abspath(__file__))

SECTIONS = ["Summary", "Skills", "Work Experience", "Projects", "Education", "Certifications"]
ACTION_VERBS = {
    "designed", "developed", "built", "engineered", "architected", "implemented", "led", "executed", "delivered",
    "launched", "resolved", "achieved", "championed", "mentored", "optimized", "optimised", "automated", "integrated",
    "migrated", "reduced", "improved", "owned", "directed", "managed", "planned", "established", "secured",
    "streamlined", "spearheaded", "created", "deployed", "orchestrated", "drove", "shipped", "scaled", "refactored",
    "introduced", "modernized", "accelerated", "enabled", "transformed", "cut", "increased", "boosted", "pioneered",
}
PRONOUNS = {"i", "me", "my", "we", "our", "us", "them", "their", "they"}
STOP = set("""a an the and or of to in on for with by via from across at as into over under per is are was were be been
using used while within through end-to-end end to that this these those its it their them so all any each every both
plus not no than more most less least out up down off""".split())
# Technology terms may legitimately repeat (ATS rewards it); only non-tech words are checked for repetition.
CORE_STACK_OK = {"java", "spring", "boot", "apis", "api", "rest", "react.js", "react", "aws", "services", "service", "production",
                 "microservices", "backend", "frontend", "data", "hibernate", "postgresql", "mysql", "kafka", "graphql", "docker",
                 "kubernetes", "jenkins", "redis", "typescript", "javascript", "security", "cloud", "features", "engineer",
                 "software", "systems", "system", "design", "testing", "unit", "integration", "development", "developer"}
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9+./#%-]*")


def words(s):
    return WORD_RE.findall(s)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    pdf = sys.argv[1]
    jd = sys.argv[sys.argv.index("--jd") + 1] if "--jd" in sys.argv else None
    png = sys.argv[sys.argv.index("--png") + 1] if "--png" in sys.argv else None

    doc = fitz.open(pdf)
    page = doc[0]
    text = page.get_text()
    fails, warns, oks = [], [], []

    def check(cond, msg, warn=False):
        (oks if cond else (warns if warn else fails)).append(msg)

    # 1 page
    check(len(doc) == 1, f"pages = {len(doc)} (must be 1)")

    # word count
    wc = len(words(text))
    check(480 <= wc <= 680, f"words = {wc} (target 480-680)", warn=True)

    # text extraction sanity
    bad_glyphs = sorted({c for c in text if ord(c) > 0x2FF and c not in "+\u2014"})
    check(not bad_glyphs, f"non-Latin glyphs in extraction: {bad_glyphs} (digits/fonts broken for ATS)")
    digits_ok = re.search(r"\b20\d\d\b", text) and re.search(r"\d+%", text)
    check(bool(digits_ok), "years and percentages extract as real digits")
    glued = [w for w in words(text) if re.search(r"[a-z]{3,}[A-Z][a-z]{2,}", w)
             and w not in {"GraphQL", "PostgreSQL", "MySQL", "GitHub", "JavaScript", "TypeScript", "OpenAPI", "MinIO",
                           "QuickBooks", "RESTful", "LinkedIn", "DevOps", "GenAI", "SaaS", "WebFlux", "DynamoDB", "MongoDB"}
             and "/" not in w]
    check(not glued, f"glued words (spaces lost): {glued[:8]}")
    check(not re.search(r"\w-\n\w", text), "no hyphenated line breaks")

    # sections
    missing = [s for s in SECTIONS if not re.search(rf"(?m)^{re.escape(s)}\s*$", text)]
    check(not missing, f"section headings present (missing: {missing})")

    # bullets: action verbs & pronouns
    bullets = [l.strip() for l in text.splitlines() if l.strip().startswith("\u2022")]
    weak = [b.split()[1] for b in bullets if len(b.split()) > 1 and b.split()[1].lower().strip(",.") not in ACTION_VERBS]
    check(not weak, f"all {len(bullets)} bullets start with an approved action verb (weak: {weak})")
    pron = sorted({w.lower() for w in re.findall(r"\b[A-Za-z]+\b", text) if w.lower() in PRONOUNS})
    check(not pron, f"no personal pronouns (found: {pron})")

    # repetition
    freq = {}
    for w in re.findall(r"\b[A-Za-z][A-Za-z-]+\b", text):
        lw = w.lower()
        if lw in STOP or lw in CORE_STACK_OK or len(lw) < 4:
            continue
        freq[lw] = freq.get(lw, 0) + 1
    rep = {k: v for k, v in freq.items() if v > 4}
    check(not rep, f"no word repeated >4x (found: {rep})", warn=True)

    # bold ratio
    bold = 0
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if "Bold" in s["font"] or (s["flags"] & 16):
                    bold += len(words(s["text"]))
    ratio = bold / max(wc, 1)
    check(0.08 <= ratio <= 0.15, f"bold ratio = {ratio:.0%} (target 8-15%)", warn=True)

    # fonts embedded
    fonts = {f[3] for f in page.get_fonts()}
    check(all("+" in f for f in fonts), f"fonts embedded/subsetted: {sorted(fonts)}")

    # contact
    check(bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)), "email present")
    check(bool(re.search(r"\+?\d[\d\s-]{8,}\d", text)), "phone present")

    # JD coverage
    coverage_line = ""
    if jd:
        out = subprocess.run([sys.executable, os.path.join(HERE, "jd_keywords.py"), jd, "--json"],
                             capture_output=True, text=True)
        import json
        kw = json.loads(out.stdout)
        low = text.lower()

        norm = re.sub(r"[-\u2013\u2014]", " ", low)          # hyphens -> spaces ("unit-test" -> "unit test")
        norm_nospace = norm.replace(" ", "")

        def present(item):
            key = item["keyword"]
            m = re.match(r"(?i)java\s*(\d+)$", key)
            if m:  # "Java 11" satisfied by "Java 8/11/17/21"
                return re.search(rf"java[^\n.;]{{0,15}}\b{m.group(1)}\b", low) is not None
            cands = {key.lower(), item["jd_spelling"].lower()}
            cands |= {c.replace(".js", "") for c in cands}
            cands |= {re.sub(r"[-\u2013]", " ", c) for c in cands}
            cands |= {c[:-3] for c in cands if c.endswith("ing")}   # "unit testing" -> "unit test"
            cands |= {c.rstrip("s") for c in cands}
            return any(c in norm or c.replace(" ", "") in norm_nospace for c in cands if len(c) > 2)

        req = kw["required"]; pref = kw["preferred"]; other = kw["other"]
        req_hit = [i["keyword"] for i in req if present(i)]
        req_miss = [i["keyword"] for i in req if not present(i)]
        all_items = req + pref + other
        all_hit = [i["keyword"] for i in all_items if present(i)]
        all_miss = [i["keyword"] for i in all_items if not present(i)]
        r_cov = len(req_hit) / max(len(req), 1)
        a_cov = len(all_hit) / max(len(all_items), 1)
        check(r_cov >= 0.90, f"REQUIRED keyword coverage {r_cov:.0%} ({len(req_hit)}/{len(req)}) - missing: {req_miss}")
        check(a_cov >= 0.75, f"overall keyword coverage {a_cov:.0%} ({len(all_hit)}/{len(all_items)}) - missing: {all_miss}", warn=True)
        title = kw.get("title", "")
        if title:
            check(title.lower() in low, f"JD title '{title}' appears in resume", warn=True)
        coverage_line = f" | JD coverage: required {r_cov:.0%}, overall {a_cov:.0%}"

    if png:
        page.get_pixmap(dpi=110).save(png)
        oks.append(f"rendered page 1 -> {png}")

    for m in oks:
        print("OK ", m)
    for m in warns:
        print("WARN ", m)
    for m in fails:
        print("FAIL ", m)
    status = "PASS" if not fails else "FAIL"
    print(f"\nRESULT: {status} | pages={len(doc)} words={wc} bold={ratio:.0%}{coverage_line}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
