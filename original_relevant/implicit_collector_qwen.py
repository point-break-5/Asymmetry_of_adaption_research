

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

ANSWER_MODEL_NAME = "Qwen3.6-27B"
ANSWER_MODEL_ID   = "qwen/qwen3.6-27b"
MAX_WORKERS       = 6

SYSTEM_PROMPT = "You are a helpful assistant."

INPUT_TSV  = os.path.join(HERE, "implicitdataset.tsv") #replace with your file name and directory where applicable
OUTPUT_TSV = os.path.join(HERE, "implicitqwen.tsv")

write_lock = threading.Lock()


def get_answer(question):
    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=ANSWER_MODEL_ID,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": question},
                ],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            wait = (2 ** attempt) * 5
            print(f"  ! Error [{ANSWER_MODEL_NAME}]: {e}")
            print(f"  ! Retrying in {wait}s (attempt {attempt+1}/4)")
            time.sleep(wait)
    return "ERROR"


def worker(row):
    answer = get_answer(row["Generated_Question"])
    return {
        "No":                 row["No"],
        "ID":                 row["ID"],
        "Domain":             row["Domain"],
        "Topic":              row["Topic"],
        "Topic_Details":      row["Topic_Details"],
        "Source_Law":         row["Source_Law"],
        "Question_Model":     row["Model_Name"],
        "Literacy_Level":     row["Literacy_Level"],
        "Generated_Question": row["Generated_Question"],
        "Answer_Model":       ANSWER_MODEL_NAME,
        "LLM_Response":       answer,
    }


def main():
    df_questions = pd.read_csv(INPUT_TSV, sep="\t")

    if os.path.exists(OUTPUT_TSV) and os.path.getsize(OUTPUT_TSV) > 0:
        df_done = pd.read_csv(OUTPUT_TSV, sep="\t")
        results = df_done.to_dict("records")
        done_keys = set(zip(df_done["ID"], df_done["Literacy_Level"]))
        print(f"Resuming: {len(done_keys)} rows already done\n")
    else:
        results = []
        done_keys = set()

    tasks = []
    for _, row in df_questions.iterrows():
        key = (row["ID"], row["Literacy_Level"])
        if key not in done_keys:
            tasks.append(row.to_dict())

    total_target = len(df_questions)
    print(f"Queued {len(tasks)} tasks (target total {total_target}) | {MAX_WORKERS} workers\n")

    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(worker, t): t for t in tasks}
        for fut in as_completed(futures):
            t = futures[fut]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"  ! worker exception No.{t.get('No')}: {e}")
                continue

            with write_lock:
                results.append(rec)
                completed += 1
                if rec["LLM_Response"] != "ERROR":
                    done_keys.add((rec["ID"], rec["Literacy_Level"]))
                print(f"[{len(done_keys)}/{total_target}] No.{rec['No']} | {rec['ID']} | {rec['Literacy_Level']}")
                if completed % 4 == 0:
                    pd.DataFrame(results).to_csv(OUTPUT_TSV, sep="\t", index=False)

    pd.DataFrame(results).to_csv(OUTPUT_TSV, sep="\t", index=False)
    print(f"\nDone. {len(results)} rows saved to {OUTPUT_TSV}")


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY not set in .env")
        exit(1)
    main()
