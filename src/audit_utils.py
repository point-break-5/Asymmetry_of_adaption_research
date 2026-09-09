from __future__ import annotations

import json
import math
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

CLEANING_REPLACEMENTS = [
    ("-->", " leads to "), ("=>", " leads to "), ("→", " leads to "),
    ("►", " leads to "), ("▼", " then "), ("▲", " then "), ("←", " comes from "),
]


def remove_emoji(text: str) -> str:
    emoji_pattern = re.compile(
        "[" u"\\U0001F600-\\U0001F64F" u"\\U0001F300-\\U0001F5FF"
        u"\\U0001F680-\\U0001F9FF" u"\\U00002700-\\U000027BF"
        u"\\U0001FA00-\\U0001FA6F" u"\\U00002500-\\U00002BFF"
        u"\\U00002600-\\U000026FF" u"✀-➿" u"⌀-⏏" 
        "✓✗⚠►▸▼▲◄→←↑↓│├└┌┐┘┤┬┴┼"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(" ", str(text))


def replace_arrows(text: str) -> str:
    text = str(text)
    for arrow, repl in CLEANING_REPLACEMENTS:
        text = text.replace(arrow, repl)
    return text


def extract_code_block_content(text: str) -> str:
    def clean_block(match):
        code = match.group(1)
        code = ''.join(' ' if 0x2500 <= ord(ch) <= 0x257F else ch for ch in code)
        code = re.sub(r'[ \t]+', ' ', code)
        code = re.sub(r'\n{2,}', '\n', code)
        return code.strip()
    return re.sub(r'```(?:\w+)?\n?(.*?)```', clean_block, str(text), flags=re.DOTALL)


def convert_table_to_text_safe(text: str) -> str:
    lines = str(text).split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('|') and line.endswith('|'):
            if re.match(r'^\|[\s\-:]+\|$', line):
                i += 1
                continue
            cells = [c.strip() for c in line.strip('|').split('|') if c.strip()]
            if i + 1 < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i + 1].strip()):
                headers = cells
                i += 2
                while i < len(lines):
                    row = lines[i].strip()
                    if not (row.startswith('|') and row.endswith('|')):
                        break
                    values = [c.strip() for c in row.strip('|').split('|') if c.strip()]
                    headers = [re.sub(r'\*+(.+?)\*+', r'\1', h) for h in headers]
                    values = [re.sub(r'\*+(.+?)\*+', r'\1', v) for v in values]
                    pairs = [f"{h} is {v}" for h, v in zip(headers, values) if h and v]
                    if pairs:
                        result.append('. '.join(pairs) + '.')
                    i += 1
            else:
                result.append('. '.join(cells) + '.')
                i += 1
        else:
            result.append(lines[i])
            i += 1
    return '\n'.join(result)


def remove_markdown_dividers(text: str) -> str:
    return re.sub(r'^\s*[-_*]{2,}\s*$', '', str(text), flags=re.MULTILINE)


def ensure_line_terminators(text: str) -> str:
    out = []
    for line in str(text).split('\n'):
        stripped = line.strip()
        if not stripped:
            out.append('')
            continue
        if re.match(r'^(?:-|\*|•|\d+[.)])\s+', stripped) and not re.search(r'[.!?:;]$', stripped):
            out.append(stripped + '.')
        else:
            out.append(line)
    return '\n'.join(out)


def clean_response(text: str) -> str:
    text = remove_emoji(text)
    text = replace_arrows(text)
    text = extract_code_block_content(text)
    text = convert_table_to_text_safe(text)
    text = remove_markdown_dividers(text)
    text = ensure_line_terminators(text)
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def load_qwen_sources(root: str | Path) -> dict[str, pd.DataFrame]:
    root = Path(root)
    return {
        'explicit': pd.read_csv(root/'explicitqwen.tsv', sep='\t'),
        'implicit': pd.read_csv(root/'implicitqwen.tsv', sep='\t'),
        'explicit_extraction': pd.read_csv(root/'qwen_explicit_extraction.tsv', sep='\t'),
        'implicit_extraction': pd.read_csv(root/'qwen_implicit_extraction.tsv', sep='\t'),
        'explicit_events': pd.read_csv(root/'explicitdataset.tsv', sep='\t'),
        'implicit_questions': pd.read_csv(root/'implicitdataset.tsv', sep='\t'),
    }


def normalize_level(x: str) -> str:
    return str(x).strip()


def make_explicit_user_prompt(row: pd.Series) -> str:
    persona = normalize_level(row['Literacy_Level'])
    desc = {
        'High Literacy': 'I have high literacy on this topic. Explain the topic according to my level.',
        'Mid Literacy': 'I have mid literacy on this topic. Explain the topic according to my level.',
        'Low Literacy': 'I have low literacy on this topic. Explain the topic according to my level.',
    }[persona]
    return (
        f"The topic: {row['Topic']}\n"
        f"Additional context/details: {row['Topic_Details']}\n"
        f"Source/Reference: {row['Source_Law']}\n"
        f"Persona: {desc} ({persona})"
    )


def build_eval_rows(data: dict[str, pd.DataFrame], event_ids: set[str] | None = None) -> pd.DataFrame:
    ex = data['explicit'].copy()
    im = data['implicit'].copy()
    if event_ids is not None:
        ex = ex[ex['ID'].astype(str).isin(event_ids)].copy()
        im = im[im['ID'].astype(str).isin(event_ids)].copy()
    ex['Condition'] = 'Explicit'
    ex['Eval_User_Input'] = ex.apply(make_explicit_user_prompt, axis=1)
    ex['History_Response'] = ex['LLM_Response'].astype(str)
    ex['History_Model'] = ex['Model_Name'].astype(str)
    im['Condition'] = 'Implicit'
    im['Eval_User_Input'] = im['Generated_Question'].astype(str)
    im['History_Response'] = im['LLM_Response'].astype(str)
    im['History_Model'] = im['Answer_Model'].astype(str)
    cols = ['ID','Domain','Topic','Topic_Details','Source_Law','Condition','Literacy_Level','Eval_User_Input','History_Response','History_Model']
    common = pd.concat([ex[cols], im[cols]], ignore_index=True)
    return common.sort_values(['ID','Condition','Literacy_Level']).reset_index(drop=True)


def make_sft_records(data: dict[str, pd.DataFrame], train_ids: set[str]) -> list[dict]:
    records = []
    ex = data['explicit']
    im = data['implicit']
    for _, r in ex[ex['ID'].astype(str).isin(train_ids)].iterrows():
        records.append({
            'event_id': str(r['ID']), 'condition': 'Explicit', 'literacy_level': str(r['Literacy_Level']),
            'messages': [
                {'role': 'system', 'content': "You are a helpful assistant that adapts to the user's literacy level."},
                {'role': 'user', 'content': make_explicit_user_prompt(r)},
                {'role': 'assistant', 'content': str(r['LLM_Response'])},
            ]
        })
    for _, r in im[im['ID'].astype(str).isin(train_ids)].iterrows():
        records.append({
            'event_id': str(r['ID']), 'condition': 'Implicit', 'literacy_level': str(r['Literacy_Level']),
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': str(r['Generated_Question'])},
                {'role': 'assistant', 'content': str(r['LLM_Response'])},
            ]
        })
    return records


def split_event_ids(data: dict[str, pd.DataFrame], test_frac=.2, seed=42):
    ids = sorted(set(data['explicit']['ID'].astype(str)) & set(data['implicit']['ID'].astype(str)))
    rng = random.Random(seed)
    rng.shuffle(ids)
    n_test = max(1, round(len(ids) * test_frac))
    test_ids = set(ids[:n_test])
    train_ids = set(ids[n_test:])
    return sorted(train_ids), sorted(test_ids)


def long_to_wide_level(df: pd.DataFrame, value_cols: Sequence[str]) -> pd.DataFrame:
    idx = ['ID','Condition']
    w = df.pivot_table(index=idx, columns='Literacy_Level', values=list(value_cols), aggfunc='first')
    w.columns = [f'{m}__{lvl}' for m,lvl in w.columns]
    return w.reset_index()


def compute_paired_stats(df: pd.DataFrame, metric: str, lower_is_better: bool, pair=('High Literacy','Low Literacy')) -> pd.DataFrame:
    from scipy.stats import ttest_rel
    a, b = pair
    rows = []
    for condition in sorted(df['Condition'].unique()):
        s = df[df['Condition'] == condition]
        piv = s.pivot_table(index=['ID'], columns='Literacy_Level', values=metric, aggfunc='first')
        if a not in piv.columns or b not in piv.columns:
            continue
        x = pd.to_numeric(piv[a], errors='coerce')
        y = pd.to_numeric(piv[b], errors='coerce')
        keep = x.notna() & y.notna()
        x = x[keep].to_numpy(); y = y[keep].to_numpy()
        d = x - y if not lower_is_better else y - x
        # direction here is “better-preserving” for content metrics when lower_is_better=False
        t, p = ttest_rel(x, y, alternative='greater' if not lower_is_better else 'less')
        sd = d.std(ddof=1) if len(d) > 1 else np.nan
        effect = d.mean() / sd if sd and np.isfinite(sd) else np.nan
        rows.append({'Condition':condition,'Metric':metric,'n':len(d),'Mean_High':x.mean(),'Mean_Low':y.mean(),'Mean_HighMinusLow':x.mean()-y.mean(),'t':t,'p':p,'Cohen_d_paired_directional':effect})
    return pd.DataFrame(rows)


def safe_mean(frame, col):
    return float(pd.to_numeric(frame[col], errors='coerce').mean()) if len(frame) else float('nan')


def summarize_metrics(df: pd.DataFrame, metric_cols: Sequence[str]) -> pd.DataFrame:
    return df.groupby(['ModelStage','Condition','Literacy_Level'])[list(metric_cols)].mean().reset_index()


def export_markdown_table(df: pd.DataFrame, path: str | Path):
    Path(path).write_text(df.to_markdown(index=False), encoding='utf-8')


def deterministic_seed(seed=42):
    random.seed(seed); np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
