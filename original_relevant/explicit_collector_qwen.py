

import os
import time
import threading
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

MODEL_NAME  = "Qwen3.6-27B"
MODEL_ID    = "qwen/qwen3.6-27b"
MAX_WORKERS = 4

PERSONAS = [
    {"level": "High Literacy",
     "description": "I have high literacy on this topic. Explain the topic according to my level.",
     "system_instruction": "You are a helpful assistant that adapts to the user's literacy level."},
    {"level": "Mid Literacy",
     "description": "I have mid literacy on this topic. Explain the topic according to my level.",
     "system_instruction": "You are a helpful assistant that adapts to the user's literacy level."},
    {"level": "Low Literacy",
     "description": "I have low literacy on this topic. Explain the topic according to my level.",
     "system_instruction": "You are a helpful assistant that adapts to the user's literacy level."},
]

INPUT_TSV  = os.path.join(HERE, "explicitdataset.tsv") #replace with your file name and directory where applicable
OUTPUT_TSV = os.path.join(HERE, "explicitqwen.tsv")

write_lock = threading.Lock()


def call_model(topic, topic_details, topic_source, persona_desc, persona_level, system_instruction):
    prompt = f"""The topic: {topic}
Additional context/details: {topic_details}
Source/Reference: {topic_source}
Persona: {persona_desc} ({persona_level})
"""
    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user",   "content": prompt},
                ],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            wait = (2 ** attempt) * 5
            print(f"  ! Error [{MODEL_NAME}]: {e}")
            print(f"  ! Retrying in {wait}s (attempt {attempt+1}/4)")
            time.sleep(wait)
    return "ERROR"


def worker(task):
    """task = (topic_id, row_dict, persona)."""
    topic_id, row, persona = task
    response = call_model(
        row["Event/Topic"], row["Details"], row["Source/Reference"],
        persona["description"], persona["level"], persona["system_instruction"],
    )
    return {
        "ID":             topic_id,
        "Domain":         row["Domain"],
        "Topic":          row["Event/Topic"],
        "Topic_Details":  row["Details"],
        "Source_Law":     row["Source/Reference"],
        "Model_Name":     MODEL_NAME,
        "Literacy_Level": persona["level"],
        "LLM_Response":   response,
    }


def main():
    df_events = pd.read_csv(INPUT_TSV, sep="\t")

    if os.path.exists(OUTPUT_TSV) and os.path.getsize(OUTPUT_TSV) > 0:
        df_done = pd.read_csv(OUTPUT_TSV, sep="\t")
        results = df_done.to_dict("records")
        done_keys = set(zip(df_done["ID"], df_done["Model_Name"], df_done["Literacy_Level"]))
        print(f"Resuming: {len(done_keys)} rows already done\n")
    else:
        results = []
        done_keys = set()

    tasks = []
    for _, row in df_events.iterrows():
        for persona in PERSONAS:
            key = (row["ID"], MODEL_NAME, persona["level"])
            if key not in done_keys:
                tasks.append((row["ID"], row.to_dict(), persona))

    total_target = len(df_events) * len(PERSONAS)
    print(f"Queued {len(tasks)} tasks (target total {total_target}) | {MAX_WORKERS} workers\n")

    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(worker, t): t for t in tasks}
        for fut in as_completed(futures):
            t = futures[fut]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"  ! worker exception {t[0]}/{t[2]['level']}: {e}")
                continue

            with write_lock:
                results.append(rec)
                completed += 1
                if rec["LLM_Response"] != "ERROR":
                    done_keys.add((rec["ID"], rec["Model_Name"], rec["Literacy_Level"]))
                print(f"[{len(done_keys)}/{total_target}] {rec['ID']} | {rec['Literacy_Level']}")
                if completed % 4 == 0:
                    pd.DataFrame(results).to_csv(OUTPUT_TSV, sep="\t", index=False)

    pd.DataFrame(results).to_csv(OUTPUT_TSV, sep="\t", index=False)
    print(f"\nDone. {len(results)} rows saved to {OUTPUT_TSV}")


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY not set in .env")
        exit(1)
    main()
