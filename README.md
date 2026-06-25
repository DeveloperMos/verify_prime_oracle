# verify_prime_oracle

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
