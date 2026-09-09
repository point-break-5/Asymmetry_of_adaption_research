

import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import google.generativeai as genai

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not set in .env")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)

EXTRACTOR_MODEL = "gemini-3.1-flash-lite-preview"
MAX_WORKERS     = 5

write_lock = threading.Lock()

SYSTEM_PROMPT = """You are a precise fact extraction engine.
Read the entire LLM response carefully to understand its meaning. Then extract every SPECIFIC fact according to the category definitions below.

EXTRACTION CATEGORIES — SPECIFIC FACTS
- LAW/POLICY_NAME : Named law, act, ordinance, or regulation with its official title e.g., "GDPR", "ICCPR", "Bank Company Act 1991", "TikTok US Privacy Policy"
- SECTION_REF : Section, article, clause, or chapter WITH its number e.g., "Section 45", "Article 14(3)(g)", "Chapter IV"
- ORG_NAME : Named organization, institution, company, regulatory body, or court etc — full name or recognized acronym e.g., "ILO", "WHO", "BTRC", "Bangladesh Bank", "Meta"
- PENALTY_SPECIFIC : Punishment with a specific type or number e.g., "5 years imprisonment", "death penalty", "life sentence"
- AMOUNT_SPECIFIC : Monetary figure with number and currency e.g., "50,000 taka", "$500", "50 lakh taka"
- TIME_SPECIFIC : Duration, timeline or deadline with a specific number e.g., "within 30 days", "6 months", "3 years"
- MEASURE_SPECIFIC : Quantity, percentage, or threshold with a specific number e.g., "75% of wages", "2.5 km radius"
- SCIENCE_TERM : Named scientific term, compound, pathogen, or substance e.g., "N1-methylpseudouridine", "PM2.5", "mRNA", "Content Delivery Networks (CDNs)"
- STANDARD_NAME : Named standard, protocol, code of practice, or treaty e.g., "ISO 27001", "CAC/RCP 57-2004", "Geneva Convention"
- CASE_LAW : Named legal case with parties and/or year e.g., "Goodwin v. United Kingdom (1996)"
- CONDITION_NAME : Named disease, disorder, or medical condition e.g., "Type 2 Diabetes", "Q fever", "PTSD"
- PERSON_NAME : Named real individual (not fictional) e.g., "Katalin Karikó", "Drew Weissman"
- DATE_SPECIFIC : Specific calendar year or date appearing as a standalone temporal reference — NOT when the year is part of a law's official name e.g., "enacted in 2006", "adopted in 1998", "as of March 2023". IMPORTANT: "Bank Company Act 1991" → LAW_NAME only; "1991" is NOT also a DATE_SPECIFIC
- GEO_SPECIFIC : Named place, region, country, or jurisdiction appearing in a legal, regulatory, or factual context e.g., "Schengen Area", "Export Processing Zone", "Chernobyl", "Japan". But EXCLUDE: Country or place names that are part of a law's official title
- TECH_IDENTIFIER : Named technical code, product ID, name or identifier e.g., "BNT162b2", "H300", "16 AWG", "GHS06", "TLR7", "29 CFR 1910.146", "JSON"
- NUMERIC_THRESHOLD : Specific operational or safety number that is not money, time, or penalty e.g., "8,000 feet", "100–120 compressions/min", "19.5% oxygen"
- OTHER_SPECIFIC : A clearly specific, named, or quantified real-world fact that may not fit any category above. e.g., "IPv4", "TCP/IP", "3-tier architecture", "Grade 7 steel", "Personal Protective Equipment (PPE)", "Lockout/Tagout (LOTO)", "cardiopulmonary resuscitation (CPR)". Only extract when it is specific and real.

WHAT TO SKIP
Skip anything that lacks specificity:
- Duplicate mentions of the same fact — Same text in the same category or different category → count ONCE only, no matter how many times it appears
- "the law", "the act", "the court","global norms" , "the relevant section", "Terms of Service"  — but no specific name, number, duration or service name value given
- Formatting markers, emojis

IMPORTANT DISTINCTIONS
-If the LLM writes "for example, the Income Tax Ordinance 1984 requires..." — this is a real named law cited as an example. EXTRACT IT. Only skip invented fictional scenarios where no real entity is being named (e.g., "imagine a law called the Sunshine Act").
- "Bangladesh Labour Act 2006" = 1 fact (LAW_NAME)
- "Section 45 of Bangladesh Labour Act 2006" = 2 facts (LAW_NAME + SECTION_REF, counted separately)
- "GDPR Article 17" = 2 facts (LAW_NAME + SECTION_REF)
- If an acronym and its full form refer to the same entity ANYWHERE in the response — whether adjacent or paragraphs apart — count as ONE fact  e.g., Biometric Information Privacy Act (BIPA) count it as one if it means the same thing and mentioned together.
- Same fact mentioned 5 times → count ONCE only
- "Section 45" AND "Section 46" = 2 facts (different sections)
- "ILO" AND "WHO" = 2 facts (different orgs)
- Year embedded in a law name ("Bank Company Act 1991") → 1 fact as LAW_NAME; the year is NOT also a DATE_SPECIFIC
- "50,000 taka fine for first offence, 1,00,000 taka for repeat" = 2 facts (two different AMOUNT_SPECIFIC values)
- "Goodwin v. United Kingdom (1996)" = 1 fact (CASE_LAW only)
  "United Kingdom" and "1996" are NOT extracted separately
- "Bangladesh Labour Act 2006" = 1 fact (LAW_NAME only) here "Bangladesh" is NOT also GEO_SPECIFIC as it is part of the name of the law

ANTI-SHORTCUT WARNING
- Do NOT mechanically scan. Read carefully and ask: "Is this a named, specific, real-world entity or quantity?"
  Only then extract.
- If a specific fact is already fully contained within a larger extracted fact or has repetition, do not extract it again as a separate fact.

OUTPUT FORMAT — follow exactly.
Provide the total count first, then the list of extracted facts separated by SEMICOLONS.
Do not include category labels (like ORG_NAME:) in the list. Follow the format below.

SPECIFIC_COUNT: [number]
SPECIFIC_LIST: fact 1; fact 2; fact 3;
"""

USER_PROMPT_TEMPLATE = "Extract all specific facts from the following paragraph.\n\n{response}"


def parse_output(text: str) -> dict:
    result = {"specific_count": 0, "specific_list": ""}
    items = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "SPECIFIC_COUNT" in line:
            try:
                result["specific_count"] = int(line.split(":")[1].strip())
            except Exception:
                pass
        elif "SPECIFIC_LIST" in line:
            rest = line.replace("SPECIFIC_LIST:", "").strip()
            all_text = rest
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if "SPECIFIC_COUNT" in nxt or nxt == "":
                    break
                all_text += " " + nxt
                i += 1
            raw_items = [x.strip() for x in all_text.split(";") if x.strip()]
            for item in raw_items:
                if ":" in item:
                    cleaned = item.split(":", 1)[1].strip()
                    if cleaned:
                        items.append(cleaned)
                else:
                    items.append(item)
            continue
        i += 1
    result["specific_list"] = " | ".join(items)
    return result


def extract_facts(llm_response: str) -> dict:
    prompt = USER_PROMPT_TEMPLATE.format(response=llm_response)
    for attempt in range(4):
        try:
            model = genai.GenerativeModel(
                model_name=EXTRACTOR_MODEL,
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(temperature=0.0),
            )
            resp = model.generate_content(prompt)
            return parse_output(resp.text.strip())
        except Exception as e:
            wait = (2 ** attempt) * 3
            print(f"  ! Gemini error: {e} — retrying in {wait}s ({attempt+1}/4)")
            time.sleep(wait)
    return {"specific_count": -1, "specific_list": "ERROR"}


def process_row_explicit(row, i, total):
    print(f"[{i+1}/{total}] {row['ID']} | {row['Literacy_Level']}")
    extracted = extract_facts(str(row["LLM_Response"]))
    return {
        "No":             i + 1,
        "ID":             row["ID"],
        "Domain":         row["Domain"],
        "Topic":          row["Topic"],
        "Topic_Details":  row["Topic_Details"],
        "Source_Law":     row["Source_Law"],
        "Model_Name":     row["Model_Name"],
        "Literacy_Level": row["Literacy_Level"],
        "Specific_Count": extracted["specific_count"],
        "Specific_List":  extracted["specific_list"],
    }


def process_row_implicit(row, i, total):
    print(f"[{i+1}/{total}] {row['ID']} | {row['Literacy_Level']} | Q-gen: {row['Question_Model']}")
    extracted = extract_facts(str(row["LLM_Response"]))
    return {
        "No":                 row.get("No", i + 1),
        "ID":                 row["ID"],
        "Domain":             row["Domain"],
        "Topic":              row["Topic"],
        "Topic_Details":      row["Topic_Details"],
        "Source_Law":         row["Source_Law"],
        "Question_Model":     row["Question_Model"],
        "Answer_Model":       row["Answer_Model"],
        "Generated_Question": row["Generated_Question"],
        "Literacy_Level":     row["Literacy_Level"],
        "Specific_Count":     extracted["specific_count"],
        "Specific_List":      extracted["specific_list"],
    }


def run_extractor(input_tsv, output_tsv, process_fn):
    df = pd.read_csv(input_tsv, sep="\t")

    if os.path.exists(output_tsv) and os.path.getsize(output_tsv) > 0:
        df_done = pd.read_csv(output_tsv, sep="\t")
        done_keys = set(zip(df_done["ID"], df_done["Literacy_Level"]))
        results = df_done.to_dict("records")
        print(f"Resuming: {len(done_keys)} rows already extracted")
    else:
        done_keys = set()
        results = []

    rows_to_process = [
        (i, row) for i, (_, row) in enumerate(df.iterrows())
        if (row["ID"], row["Literacy_Level"]) not in done_keys
    ]
    total = len(df)
    print(f"To extract: {len(rows_to_process)} / total {total}")
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_fn, row, i, total): (i, row)
            for i, row in rows_to_process
        }
        for future in as_completed(futures):
            result = future.result()
            with write_lock:
                results.append(result)
                completed += 1
                if completed % 4 == 0:
                    pd.DataFrame(results).to_csv(output_tsv, sep="\t", index=False)
                    print(f"  --- Checkpoint: {completed} done ---")

    pd.DataFrame(results).to_csv(output_tsv, sep="\t", index=False)
    print(f"\nDone. Saved {len(results)} rows to {output_tsv}\n")


def main():
    print("PASS 1/2 — Explicit-condition")
    run_extractor(
        os.path.join(HERE, "explicitqwen.tsv"), #Change this if your implicit file data  in a different file
        os.path.join(HERE, "explicitqwen_extraction.tsv"), #Change this if you want the output in a different file
        process_row_explicit,
    )

    print("PASS 2/2 — Implicit-condition Qwen")
    run_extractor(
        os.path.join(HERE, "implicit_qwen.tsv"),  #Change this if your implicit file data  in a different file
        os.path.join(HERE, "implicit_qwen_extraction.tsv"), #Change this if you want the output in a different file
        process_row_implicit,
    )


if __name__ == "__main__":
    main()
