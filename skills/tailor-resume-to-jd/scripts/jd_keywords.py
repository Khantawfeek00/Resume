#!/usr/bin/env python3
"""Extract ATS keywords from a job description.

Usage:
    python3 jd_keywords.py jd/company-role.txt          # human-readable report
    python3 jd_keywords.py jd/company-role.txt --json   # machine-readable

Groups keywords into required / preferred / soft, reports the JD's job title,
seniority hints, and years-of-experience asks. Matching is case-insensitive and
reports the JD's own spelling so the resume can mirror it.
"""
import json
import re
import sys
from collections import OrderedDict

# Canonical skill -> accepted spellings/aliases (lower-case). The *JD's* spelling is what gets reported.
TECH = {
    "Java": [r"\bjava\b(?!\s*script)"],
    "Java 17": [r"\bjava\s*17\b"], "Java 21": [r"\bjava\s*21\b"], "Java 8": [r"\bjava\s*8\b"], "Java 11": [r"\bjava\s*11\b"],
    "Spring Boot": [r"\bspring\s*boot\b"], "Spring": [r"\bspring\b(?!\s*(boot|security|data|cloud|mvc|ai|batch|webflux))"],
    "Spring MVC": [r"\bspring\s*mvc\b"], "Spring Security": [r"\bspring\s*security\b"],
    "Spring Data JPA": [r"\bspring\s*data\b", r"\bjpa\b"], "Spring Cloud": [r"\bspring\s*cloud\b"],
    "Spring AI": [r"\bspring\s*ai\b"], "Spring Batch": [r"\bspring\s*batch\b"], "Spring WebFlux": [r"\bwebflux\b", r"\breactive\b"],
    "Hibernate": [r"\bhibernate\b"], "Microservices": [r"\bmicro\s*-?\s*services?\b"],
    "REST APIs": [r"\brest(ful)?\b", r"\brest\s*apis?\b"], "GraphQL": [r"\bgraphql\b"], "gRPC": [r"\bgrpc\b"],
    "SQL": [r"\bsql\b(?!\s*server)"], "MySQL": [r"\bmysql\b"], "PostgreSQL": [r"\bpostgres(ql)?\b"], "Oracle": [r"\boracle\b"],
    "SQL Server": [r"\bsql\s*server\b)"], "MongoDB": [r"\bmongo(db)?\b"], "Cassandra": [r"\bcassandra\b"], "DynamoDB": [r"\bdynamodb\b"],
    "NoSQL": [r"\bnosql\b"], "Redis": [r"\bredis\b"], "Elasticsearch": [r"\belastic\s*search\b"],
    "Apache Kafka": [r"\bkafka\b"], "RabbitMQ": [r"\brabbitmq\b"], "Event-Driven Architecture": [r"\bevent[\s-]*driven\b", r"\bevent\s*streaming\b"],
    "AWS": [r"\baws\b", r"\bamazon\s*web\s*services\b"], "AZURE": [r"\bazure\b"], "GCP": [r"\bgcp\b", r"\bgoogle\s*cloud\b"],
    "Docker": [r"\bdocker\b"], "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"], "Jenkins": [r"\bjenkins\b"],
    "CI/CD": [r"\bci\s*/?\s*cd\b", r"\bcontinuous\s*(integration|delivery|deployment)\b"], "Git": [r"\bgit\b(?!hub|lab)"],
    "GitHub": [r"\bgithub\b"], "Maven": [r"\bmaven\b"], "Gradle": [r"\bgradle\b"], "Terraform": [r"\bterraform\b"],
    "React.js": [r"\breact(\.?js)?\b"], "Angular": [r"\bangular\b"], "Vue": [r"\bvue(\.?js)?\b"], "Node.js": [r"\bnode(\.?js)?\b"],
    "TypeScript": [r"\btypescript\b"], "JavaScript": [r"\bjavascript\b", r"\bes6\b"], "HTML5": [r"\bhtml5?\b"], "CSS3": [r"\bcss3?\b"],
    "Redux": [r"\bredux\b"], "Next.js": [r"\bnext\.?js\b"], "Full Stack": [r"\bfull[\s-]*stack\b"],
    "JUnit": [r"\bjunit\b"], "Mockito": [r"\bmockito\b"], "TDD": [r"\btdd\b", r"\btest[\s-]*driven\b"], "Unit Testing": [r"\bunit\s*test(ing|s)?\b"],
    "Swagger/OpenAPI": [r"\bswagger\b", r"\bopenapi\b"], "Postman": [r"\bpostman\b"],
    "OAuth 2.0": [r"\boauth\s*2?(\.0)?\b"], "JWT": [r"\bjwt\b"], "Keycloak": [r"\bkeycloak\b"], "Spring Security/Auth": [r"\bauthentication\b", r"\bauthorization\b"],
    "Generative AI": [r"\bgen(erative)?\s*ai\b"], "LLM": [r"\bllms?\b", r"\blarge\s*language\s*model(s)?\b"], "RAG": [r"\brag\b", r"\bretrieval[\s-]*augmented\b"],
    "Vector Database": [r"\bvector\s*(db|database|store)s?\b", r"\bpgvector\b", r"\bembeddings?\b"], "Machine Learning": [r"\bmachine\s*learning\b", r"\bml\b"],
    "GitHub Copilot": [r"\bcopilot\b"], "AI Tools": [r"\bai[\s-]*(assisted|powered|coding)\s*(tools?|development)?\b"],
    "System Design": [r"\bsystem\s*design\b"], "Distributed Systems": [r"\bdistributed\s*systems?\b"], "Design Patterns": [r"\bdesign\s*patterns?\b"],
    "Data Structures and Algorithms": [r"\bdata\s*structures?\b", r"\balgorithms?\b", r"\bdsa\b"], "OOP": [r"\boops?\b", r"\bobject[\s-]*oriented\b"],
    "SOLID": [r"\bsolid\b"], "Agile/Scrum": [r"\bagile\b", r"\bscrum\b"], "Code Review": [r"\bcode\s*reviews?\b"],
    "Performance Tuning": [r"\bperformance\s*(tuning|optimi[sz]ation)\b"], "Scalability": [r"\bscalab(le|ility)\b"], "High Availability": [r"\bhigh\s*availability\b"],
    "Production Support": [r"\bproduction\s*support\b"], "Monitoring": [r"\bmonitor(ing)?\b"], "Observability": [r"\bobservability\b"], "Grafana/Prometheus": [r"\bgrafana\b", r"\bprometheus\b", r"\bsplunk\b", r"\bdatadog\b"],
    "Linux": [r"\blinux\b", r"\bunix\b"], "Shell Scripting": [r"\bshell\s*script"], "Python": [r"\bpython\b"],
    "SaaS": [r"\bsaas\b"], "Fintech": [r"\bfintech\b"], "Payments": [r"\bpayments?\b"], "Banking": [r"\bbanking\b", r"\baccounting\b"],
    "Mentoring": [r"\bmentor(ing|ship)?\b"], "Leadership": [r"\bleadership\b", r"\blead(ing)?\s+(a\s+)?team\b"],
}

SOFT = {
    "Communication": [r"\bcommunication\b"], "Problem Solving": [r"\bproblem[\s-]*solving\b"], "Collaboration": [r"\bcollaborat"],
    "Ownership": [r"\bownership\b"], "Cross-functional": [r"\bcross[\s-]*functional\b"], "Stakeholder Management": [r"\bstakeholders?\b"],
    "Fast-paced": [r"\bfast[\s-]*paced\b"], "Self-starter": [r"\bself[\s-]*(starter|driven|motivated)\b"],
}

REQUIRED_HINTS = re.compile(r"(must[\s-]*have|required|requirements?|mandatory|essential|minimum\s+qualifications?|what\s+you.ll\s+need|you\s+have)", re.I)
PREFERRED_HINTS = re.compile(r"(nice[\s-]*to[\s-]*have|preferred|plus|bonus|good\s+to\s+have|desirable|advantage)", re.I)

TITLE_RE = re.compile(r"(?im)^(?:job\s*title|role|position|designation)\s*[:\-]\s*(.+)$")
TITLE_FALLBACK = re.compile(r"(?i)\b((senior|sr\.?|lead|principal|staff|junior)?\s*(java\s+)?(full[\s-]*stack|backend|back-end|software|application)\s*(developer|engineer|sde[\s-]*\w*)\s*(ii|iii|2|3)?)\b")
YEARS_RE = re.compile(r"(\d+)\s*(?:\+|-\s*\d+)?\s*(?:\+\s*)?years?", re.I)


def find_matches(text, table):
    """Return OrderedDict canonical -> {count, jd_spelling, required, preferred}."""
    out = OrderedDict()
    lines = text.splitlines()
    for canon, pats in table.items():
        count, spelling, req, pref = 0, None, False, False
        for pat in pats:
            rx = re.compile(pat, re.I)
            for i, line in enumerate(lines):
                for m in rx.finditer(line):
                    count += 1
                    spelling = spelling or m.group(0).strip()
                    ctx = " ".join(lines[max(0, i - 6): i + 1])  # section header context
                    if REQUIRED_HINTS.search(ctx):
                        req = True
                    if PREFERRED_HINTS.search(ctx) or PREFERRED_HINTS.search(line):
                        pref = True
        if count:
            out[canon] = {"count": count, "jd_spelling": spelling, "required": req and not pref, "preferred": pref}
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    as_json = "--json" in sys.argv
    text = open(path, encoding="utf-8", errors="ignore").read()

    tech = find_matches(text, TECH)
    soft = find_matches(text, SOFT)

    m = TITLE_RE.search(text) or TITLE_FALLBACK.search(text)
    title = (m.group(1) if m else "").strip()
    years = sorted({int(y) for y in YEARS_RE.findall(text) if int(y) <= 20})

    required = [k for k, v in tech.items() if v["required"]]
    preferred = [k for k, v in tech.items() if v["preferred"]]
    other = [k for k in tech if k not in required and k not in preferred]
    # Anything mentioned 2+ times and not marked preferred is effectively required.
    for k in other[:]:
        if tech[k]["count"] >= 2:
            required.append(k); other.remove(k)

    result = {
        "title": title, "years_of_experience": years,
        "required": [{"keyword": k, **tech[k]} for k in required],
        "preferred": [{"keyword": k, **tech[k]} for k in preferred],
        "other": [{"keyword": k, **tech[k]} for k in other],
        "soft": [{"keyword": k, **soft[k]} for k in soft],
    }
    if as_json:
        print(json.dumps(result, indent=2)); return

    print(f"JD title    : {title or '(not detected - read the JD)'}")
    print(f"Years asked : {years or '(none)'}")
    for grp in ("required", "preferred", "other", "soft"):
        items = result[grp]
        print(f"\n{grp.upper()} ({len(items)})")
        for it in sorted(items, key=lambda x: -x['count']):
            print(f"  {it['keyword']:<32} x{it['count']:<2}  JD spelling: {it['jd_spelling']}")
    print("\nNext: map each REQUIRED/PREFERRED keyword to facts.md (have / reframe / gap).")


if __name__ == "__main__":
    main()
