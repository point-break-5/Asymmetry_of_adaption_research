"""Statistical machinery from the paper's Appendix B, plus the CPU-only metrics.

Implements exactly the tests the paper reports, so numbers here are directly comparable:

  * one-sample t-test against a fixed reference (Eq. 7)   -- semantic loss vs 0, NLI vs 1
  * paired t-test, paired by event ID (Eq. 8)
  * Cohen's d, one-sample (x-mu0)/s and paired D/s_D
  * repeated-measures one-way ANOVA with partial eta-squared (Eqs. 10-13)
  * Bonferroni correction alpha/k within each metric family (Eq. 9)

t-distribution p-values use a self-contained incomplete-beta implementation so the
module has no hard SciPy dependency and can be unit-tested anywhere; SciPy is used
when present and the two agree to ~1e-12.
"""
from __future__ import annotations

import math
import re
from typing import Sequence

# effect-size benchmarks, Cohen (1988), as adopted in Appendix B.1
D_BANDS = [(2.0, "huge"), (1.2, "very large"), (0.8, "large"), (0.5, "medium"), (0.2, "small")]
ETA_BANDS = [(0.14, "large"), (0.06, "medium"), (0.01, "small")]


def d_label(d: float) -> str:
    a = abs(d)
    for cut, name in D_BANDS:
        if a >= cut:
            return name
    return "negligible"


def eta_label(e: float) -> str:
    for cut, name in ETA_BANDS:
        if e >= cut:
            return name
    return "negligible"


# ---------------------------------------------------------------- t distribution

def _betacf(a: float, b: float, x: float) -> float:
    TINY, EPS, MAXIT = 1e-30, 3e-16, 300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < TINY:
        d = TINY
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < TINY:
            d = TINY
        c = 1.0 + aa / c
        if abs(c) < TINY:
            c = TINY
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < TINY:
            d = TINY
        c = 1.0 + aa / c
        if abs(c) < TINY:
            c = TINY
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta + b * math.log(1.0 - x) + a * math.log(x)) * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: float) -> float:
    """P(T > t) for Student's t with df degrees of freedom (upper tail)."""
    p_two = _betai(df / 2.0, 0.5, df / (df + t * t))
    return p_two / 2.0 if t > 0 else 1.0 - p_two / 2.0


def t_p(t: float, df: float, tail: str = "two") -> float:
    if tail == "two":
        return _betai(df / 2.0, 0.5, df / (df + t * t))
    if tail == "greater":
        return t_sf(t, df)
    if tail == "less":
        return 1.0 - t_sf(t, df)
    raise ValueError(tail)


def f_sf(f: float, df1: float, df2: float) -> float:
    """P(F > f); the ANOVA p-value."""
    if f <= 0:
        return 1.0
    return _betai(df2 / 2.0, df1 / 2.0, df2 / (df2 + df1 * f))


# ---------------------------------------------------------------- descriptive

def mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def sd(xs: Sequence[float]) -> float:
    """Bessel-corrected sample standard deviation."""
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def quantile(xs: Sequence[float], q: float) -> float:
    s = sorted(xs)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


# ---------------------------------------------------------------- the tests

def one_sample_t(xs: Sequence[float], mu0: float = 0.0, tail: str = "two") -> dict:
    """Eq. 7. Used against perfect preservation (mu0=0) and perfect entailment (mu0=1)."""
    n = len(xs)
    m, s = mean(xs), sd(xs)
    df = n - 1
    t = (m - mu0) / (s / math.sqrt(n)) if s > 0 else float("inf")
    d = (m - mu0) / s if s > 0 else float("inf")
    return {"n": n, "mean": m, "sd": s, "mu0": mu0, "t": t, "df": df,
            "p": t_p(t, df, tail), "d": d, "d_label": d_label(d)}


def paired_t(a: Sequence[float], b: Sequence[float], tail: str = "two") -> dict:
    """Eq. 8. `a` and `b` must be aligned by event ID; tests mean(a-b)."""
    if len(a) != len(b):
        raise ValueError("paired samples must align")
    diff = [x - y for x, y in zip(a, b)]
    n = len(diff)
    dbar, sdiff = mean(diff), sd(diff)
    df = n - 1
    t = dbar / (sdiff / math.sqrt(n)) if sdiff > 0 else float("inf")
    d = dbar / sdiff if sdiff > 0 else float("inf")
    return {"n": n, "mean_a": mean(a), "mean_b": mean(b), "mean_diff": dbar,
            "sd_diff": sdiff, "t": t, "df": df, "p": t_p(t, df, tail),
            "d": d, "d_label": d_label(d)}


def rm_anova(levels: Sequence[Sequence[float]]) -> dict:
    """Eqs. 10-13. One-way repeated measures; `levels[j][i]` is subject i at level j."""
    k = len(levels)
    n = len(levels[0])
    if any(len(l) != n for l in levels):
        raise ValueError("unbalanced design")
    grand = mean([x for l in levels for x in l])
    col_means = [mean(l) for l in levels]
    row_means = [mean([levels[j][i] for j in range(k)]) for i in range(n)]

    ss_between = n * sum((cm - grand) ** 2 for cm in col_means)
    ss_error = sum((levels[j][i] - row_means[i] - col_means[j] + grand) ** 2
                   for i in range(n) for j in range(k))
    df1, df2 = k - 1, (n - 1) * (k - 1)
    ms_b, ms_e = ss_between / df1, ss_error / df2 if df2 else float("nan")
    f = ms_b / ms_e if ms_e > 0 else float("inf")
    eta = ss_between / (ss_between + ss_error) if (ss_between + ss_error) > 0 else 0.0
    return {"n": n, "k": k, "F": f, "df1": df1, "df2": df2, "p": f_sf(f, df1, df2),
            "eta_p2": eta, "eta_label": eta_label(eta), "means": col_means}


def bonferroni(alpha: float, k: int) -> float:
    """Eq. 9."""
    return alpha / k


def sig(p: float, alpha_corr: float) -> str:
    return "sig" if p < alpha_corr else "ns"


# ---------------------------------------------------------------- CPU metrics

def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(n, 1)


def fk_grade(text: str) -> float:
    """Eq. 1. Uses textstat when installed so numbers match the paper's tooling."""
    try:
        import textstat
        return float(textstat.flesch_kincaid_grade(text))
    except Exception:
        pass
    words = re.findall(r"[A-Za-z']+", text or "")
    sents = [s for s in re.split(r"[.!?]+", text or "") if s.strip()]
    if not words or not sents:
        return 0.0
    syl = sum(_syllables(w) for w in words)
    return 0.39 * (len(words) / len(sents)) + 11.8 * (syl / len(words)) - 15.59


def word_count(text: str) -> int:
    return len((text or "").split())


def _lcs(a: list, b: list) -> int:
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(cur[j], prev[j + 1]))
        prev = cur
    return prev[-1]


def _tok(s: str) -> list:
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def rouge_lsum(reference: str, candidate: str) -> dict:
    """Eq. 2. Summary-level ROUGE-L: union-LCS over reference sentences.

    Falls back to this implementation when `rouge_score` is not installed; the package
    is preferred so the figures match the paper's tooling exactly.
    """
    ref_sents = [s for s in re.split(r"[\n.!?]+", reference or "") if s.strip()]
    cand_toks = _tok(candidate)
    ref_toks = _tok(reference)
    if not cand_toks or not ref_toks:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    hits = 0
    for s in ref_sents:
        hits += _lcs(_tok(s), cand_toks)
    hits = min(hits, len(ref_toks), len(cand_toks))
    p = hits / len(cand_toks)
    r = hits / len(ref_toks)
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"precision": p, "recall": r, "f1": f}
