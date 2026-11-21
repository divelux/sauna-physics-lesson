#!/usr/bin/env python3
"""Check the sauna physics lesson files. Exit code 0 = all checks pass. Standard library only.

- every file the lesson names exists; the PDFs are Letter size with the expected page count
- the NGSS performance expectation texts are quoted the same way in every file
- index.html has one H1, a canonical link, Open Graph tags and valid JSON-LD
- every link in the HTML and Markdown files is an absolute https address or a local file that exists
- the humidity calculator appears only as optional further material
- no health claims
Works offline.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PE = {
    "MS-PS1-4": "Develop a model that predicts and describes changes in particle motion, temperature, and state of a pure substance when thermal energy is added or removed.",
    "MS-ESS2-6": "Develop and use a model to describe how unequal heating and rotation of the Earth cause patterns of atmospheric and oceanic circulation that determine regional climates.",
}
PS3B = "Energy is spontaneously transferred out of hotter regions or objects and into colder ones."
FILES = ["index.html", "lesson-plan.md", "handout.html", "handout.pdf", "answer-key.html", "answer-key.pdf",
         "print.css", "style.css", "assets/sauna-convection.svg", "README.md", "LICENSE", "LISTING.md"]
BANNED = ["detox", "toxin", "cures", "heals", "healing", "burns fat", "immune", "boosts", "boiling water is",
          "bunsen", "kettle of boiling"]
errors = []


def err(m):
    errors.append(m)


def read(n):
    return open(os.path.join(HERE, n), encoding="utf-8").read()


for f in FILES:
    if not os.path.exists(os.path.join(HERE, f)):
        err(f"missing {f}")

for name, pages in (("handout.pdf", 2), ("answer-key.pdf", 1)):
    p = os.path.join(HERE, name)
    if os.path.exists(p):
        b = open(p, "rb").read()
        n = len(re.findall(rb"/Type\s*/Page[^s]", b))
        if n != pages:
            err(f"{name}: {n} pages, expected {pages}")
        if b"612 792" not in b and not re.search(rb"MediaBox\s*\[\s*0\s+0\s+612(\.0+)?\s+792", b):
            err(f"{name}: not US Letter")

plan, page = read("lesson-plan.md"), read("index.html")
for code, text in PE.items():
    for n, s in (("lesson-plan.md", plan), ("index.html", page)):
        if text not in s:
            err(f"{n}: {code} text differs from nextgenscience.org")
for n, s in (("lesson-plan.md", plan), ("index.html", page)):
    if PS3B not in s:
        err(f"{n}: PS3.B quote missing")
    if "registered trademark of WestEd" not in s:
        err(f"{n}: NGSS trademark notice missing")

if len(re.findall(r"<h1[\s>]", page)) != 1:
    err("index.html must have exactly one h1")
for tag in ('rel="canonical"', 'property="og:title"', 'property="og:image"', 'name="description"'):
    if tag not in page:
        err(f"index.html: missing {tag}")
m = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
try:
    ld = json.loads(m.group(1))
    if ld.get("@type") != "LearningResource":
        err("JSON-LD type")
except Exception as e:  # noqa: BLE001
    err(f"JSON-LD does not parse: {e}")

for n in ("index.html", "handout.html", "answer-key.html", "lesson-plan.md", "README.md"):
    s = read(n)
    links = re.findall(r'(?:href|src)="([^"]+)"', s) + re.findall(r"\]\(([^)\s]+)\)", s)
    for u in links:
        if u.startswith(("https://", "#", "mailto:")):
            continue
        if u.startswith("http://"):
            err(f"{n}: insecure link {u}")
        elif not os.path.exists(os.path.join(HERE, u.split("#")[0])):
            err(f"{n}: broken local link {u}")
    low = s.lower()
    for b in BANNED:
        if b in low:
            err(f"{n}: banned wording '{b}'")
    for hit in re.finditer(r"sauna-humidity-calculator", s):
        before = s[max(0, hit.start() - 1500):hit.start()].lower()
        if "further material" not in before and "optional" not in before and n != "README.md":
            err(f"{n}: the humidity calculator must stay under further/optional material")

if errors:
    print("\n".join(errors))
    print(f"FAILED: {len(errors)} problem(s)")
    sys.exit(1)
print("OK: lesson files, PDFs, NGSS texts, links and page metadata check out")
