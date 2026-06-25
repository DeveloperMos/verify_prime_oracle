#!/usr/bin/env python3
"""
Reproduce the prime-gematria-sum observation on the SOLVED Liber Primus pages.
Standard library only. Run:  python3 verify_prime_oracle.py

Claim under test: in the *plaintext* of the already-solved pages, the fraction of
sentences whose Gematria-Primus value-sum is prime is far above a
structure-matched null (shuffle the runes, keep the SAME sentence lengths).
The null preserves total runes, the rune multiset, and every sentence length
(hence the parity structure) — it only randomizes which rune lands in which
sentence. So it answers "vs what baseline?" without the PNT hand-wave.
"""
import random, math, statistics

# Gematria Primus: the 29 runes and their prime values.
RUNES  = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
          73,79,83,89,97,101,103,107,109]
VAL = {r: p for r, p in zip(RUNES, PRIMES)}

# Decrypted plaintext of the solved pages (0.0, 0.1, 0.3, 0.5, 0.16), split into
# sentences (rune-only). These are the known solved text — read them if you like.
SENTENCES = [
    "ᚪᚹᚪᚱᚾᛝ","ᛒᛖᛚᛁᛖᚢᛖᚾᚩᚦᛝᚠᚱᚩᛗᚦᛁᛋᛒᚩᚩᚳ","ᛖᛉᚳᛖᛈᛏᚹᚻᚪᛏᚣᚩᚢᚳᚾᚩᚹᛏᚩᛒᛖᛏᚱᚢᛖ",
    "ᛏᛖᛋᛏᚦᛖᚳᚾᚩᚹᛚᛖᛞᚷᛖ","ᚠᛁᚾᛞᚣᚩᚢᚱᛏᚱᚢᚦ","ᛖᛉᛈᛖᚱᛁᛖᚾᚳᛖᚣᚩᚢᚱᛞᛠᚦ",
    "ᛞᚩᚾᚩᛏᛖᛞᛁᛏᚩᚱᚳᚻᚪᛝᛖᚦᛁᛋᛒᚩᚩᚳ","ᚩᚱᚦᛖᛗᛖᛋᛋᚪᚷᛖᚳᚩᚾᛏᚪᛁᚾᛖᛞᚹᛁᚦᛁᚾ",
    "ᛖᛁᚦᛖᚱᚦᛖᚹᚩᚱᛞᛋᚩᚱᚦᛖᛁᚱᚾᚢᛗᛒᛖᚱᛋ","ᚠᚩᚱᚪᛚᛚᛁᛋᛋᚪᚳᚱᛖᛞ","ᚹᛖᛚᚳᚩᛗᛖ",
    "ᚹᛖᛚᚳᚩᛗᛖᛈᛁᛚᚷᚱᛁᛗᛏᚩᚦᛖᚷᚱᛠᛏᛄᚩᚢᚱᚾᛖᚣᛏᚩᚹᚪᚱᛞᚦᛖᛖᚾᛞᚩᚠᚪᛚᛚᚦᛝᛋ",
    "ᛁᛏᛁᛋᚾᚩᛏᚪᚾᛠᛋᚣᛏᚱᛁᛈᛒᚢᛏᚠᚩᚱᚦᚩᛋᛖᚹᚻᚩᚠᛁᚾᛞᚦᛖᛁᚱᚹᚪᚣᚻᛖᚱᛖᛁᛏᛁᛋᚪᚾᛖᚳᛖᛋᛋᚪᚱᚣᚩᚾᛖ",
    "ᚪᛚᚩᛝᚦᛖᚹᚪᚣᚣᚩᚢᚹᛁᛚᛚᚠᛁᚾᛞᚪᚾᛖᚾᛞᛏᚩᚪᛚᛚᛋᛏᚱᚢᚷᚷᛚᛖᚪᚾᛞᛋᚢᚠᚠᛖᚱᛝᚣᚩᚢᚱᛁᚾᚾᚩᚳᛖᚾᚳᛖᚣᚩᚢᚱᛁᛚᛚᚢᛋᛡᚾᛋᚣᚩᚢᚱᚳᛖᚱᛏᚪᛁᚾᛏᚣᚪᚾᛞᚣᚩᚢᚱᚱᛠᛚᛁᛏᚣ",
    "ᚢᛚᛏᛁᛗᚪᛏᛖᛚᚣᚣᚩᚢᚹᛁᛚᛚᛞᛁᛋᚳᚩᚢᛖᚱᚪᚾᛖᚾᛞᛏᚩᛋᛖᛚᚠ",
    "ᛁᛏᛁᛋᚦᚱᚩᚢᚷᚻᚦᛁᛋᛈᛁᛚᚷᚱᛁᛗᚪᚷᛖᚦᚪᛏᚹᛖᛋᚻᚪᛈᛖᚩᚢᚱᛋᛖᛚᚢᛖᛋᚪᚾᛞᚩᚢᚱᚱᛠᛚᛁᛏᛁᛖᛋ",
    "ᛄᚩᚢᚱᚾᛖᚣᛞᛖᛖᛈᚹᛁᚦᛁᚾᚪᚾᛞᚣᚩᚢᚹᛁᛚᛚᚪᚱᚱᛁᚢᛖᚩᚢᛏᛋᛁᛞᛖ",
    "ᛚᛁᚳᛖᚦᛖᛁᚾᛋᛏᚪᚱᛁᛏᛁᛋᚩᚾᛚᚣᚦᚱᚩᚢᚷᚻᚷᚩᛝᚹᛁᚦᛁᚾᚦᚪᛏᚹᛖᛗᚪᚣᛖᛗᛖᚱᚷᛖ",
    "ᚹᛁᛞᛋᚩᛗ","ᚣᚩᚢᚪᚱᛖᚪᛒᛖᛝᚢᚾᛏᚩᚣᚩᚢᚱᛋᛖᛚᚠ","ᚣᚩᚢᚪᚱᛖᚪᛚᚪᚹᚢᚾᛏᚩᚣᚩᚢᚱᛋᛖᛚᚠ",
    "ᛠᚳᚻᛁᚾᛏᛖᛚᛚᛁᚷᛖᚾᚳᛖᛁᛋᚻᚩᛚᚣ","ᚠᚩᚱᚪᛚᛚᚦᚪᛏᛚᛁᚢᛖᛋᛁᛋᚻᚩᛚᚣ",
    "ᚪᚾᛁᚾᛋᛏᚱᚢᚳᛏᛡᚾᚳᚩᛗᛗᚪᚾᛞᚣᚩᚢᚱᚩᚹᚾᛋᛖᛚᚠ","ᚪᚳᚩᚪᚾ",
    "ᛞᚢᚱᛝᚪᛚᛖᛋᛋᚩᚾᚦᛖᛗᚪᛋᛏᛖᚱᛖᛉᛈᛚᚪᛁᚾᛖᛞᚦᛖᛁ","ᚦᛖᛁᛁᛋᚦᛖᚢᚩᛁᚳᛖᚩᚠᚦᛖᚳᛁᚱᚳᚢᛗᚠᛖᚱᛖᚾᚳᛖᚻᛖᛋᚪᛁᛞ",
    "ᚹᚻᛖᚾᚪᛋᚳᛖᛞᛒᚣᚪᛋᛏᚢᛞᛖᚾᛏᛏᚩᛖᛉᛈᛚᚪᛁᚾᚹᚻᚪᛏᚦᚪᛏᛗᛠᚾᛏ",
    "ᚦᛖᛗᚪᛋᛏᛖᚱᛋᚪᛁᛞᛁᛏᛁᛋᚪᚢᚩᛁᚳᛖᛁᚾᛋᛁᛞᛖᚣᚩᚢᚱᚻᛠᛞ",
    "ᛁᛞᚩᚾᛏᚻᚪᚢᛖᚪᚢᚩᛁᚳᛖᛁᚾᛗᚣᚻᛠᛞᚦᚩᚢᚷᚻᛏᚦᛖᛋᛏᚢᛞᛖᚾᛏᚪᚾᛞᚻᛖᚱᚪᛁᛋᛖᛞᚻᛁᛋᚻᚪᚾᛞᛏᚩᛏᛖᛚᛚᚦᛖᛗᚪᛋᛏᛖᚱ",
    "ᚦᛖᛗᚪᛋᛏᛖᚱᛋᛏᚩᛈᛈᛖᛞᚦᛖᛋᛏᚢᛞᛖᚾᛏᚪᚾᛞᛋᚪᛁᛞᚦᛖᚢᚩᛁᚳᛖᚦᚪᛏᛄᚢᛋᛏᛋᚪᛁᛞᚣᚩᚢᚻᚪᚢᛖᚾᚩᚢᚩᛁᚳᛖᛁᚾᚣᚩᚢᚱᚻᛠᛞᛁᛋᚦᛖᛁ",
    "ᚪᚾᛞᚦᛖᛋᛏᚢᛞᛖᚾᛏᛋᚹᛖᚱᛖᛖᚾᛚᛁᚷᚻᛏᛖᚾᛖᛞ","ᚪᚾᛖᚾᛞ","ᚹᛁᚦᛁᚾᚦᛖᛞᛖᛖᛈᚹᛖᛒ",
    "ᚦᛖᚱᛖᛖᛉᛁᛋᛏᛋᚪᛈᚪᚷᛖᚦᚪᛏᚻᚪᛋᚻᛖᛋᛏᚩ",
    "ᛁᛏᛁᛋᚦᛖᛞᚢᛏᚣᚩᚠᛖᚢᛖᚱᚣᛈᛁᛚᚷᚱᛁᛗᛏᚩᛋᛖᛖᚳᚩᚢᛏᚦᛁᛋᛈᚪᚷᛖ",
]

def gsum(s): return sum(VAL[c] for c in s)

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True

def prime_fraction(sents):
    return sum(is_prime(gsum(s)) for s in sents) / len(sents)

obs = prime_fraction(SENTENCES)
nprime = sum(is_prime(gsum(s)) for s in SENTENCES)
print(f"sentences           : {len(SENTENCES)}")
print(f"prime gematria sum  : {nprime}  ({obs:.3f})")

# Parity (the tacit assumption mortlach flagged): gematria values are almost all
# ODD primes, so even-length sentences sum to even -> never prime (except 2).
odd = [s for s in SENTENCES if gsum(s) % 2 == 1]
print(f"odd-sum sentences   : {len(odd)}/{len(SENTENCES)}"
      f"   prime among odd: {sum(is_prime(gsum(s)) for s in odd)}/{len(odd)}")

# Structure-matched empirical null: pool runes, shuffle, re-cut into the SAME
# sentence-length sequence (preserves multiset + every length + parity).
pool = [c for s in SENTENCES for c in s]
lens = [len(s) for s in SENTENCES]
random.seed(3301)
def shuffled_fraction():
    random.shuffle(pool)
    out, k = [], 0
    for L in lens:
        out.append(pool[k:k + L]); k += L
    return sum(is_prime(gsum(s)) for s in out) / len(lens)

N = 10000
null = [shuffled_fraction() for _ in range(N)]
mu, sd = statistics.mean(null), statistics.pstdev(null)
ge = sum(x >= obs for x in null)
z = (obs - mu) / sd if sd else float("inf")
print(f"\nempirical null ({N} shuffles, same lengths):")
print(f"  mean={mu:.3f}  sd={sd:.3f}  max={max(null):.3f}")
print(f"  observed={obs:.3f}  ->  z={z:.2f},  P(null>=obs)={ge}/{N}")
print("\nnote: this is a property of the PLAINTEXT (known boundaries). It does NOT")
print("crack anything and is not usable as a search oracle without the sentence")
print("boundaries — every boundary-free variant I tried fails to separate")
print("plaintext from the shuffle.")
