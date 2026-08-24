"""
Derive the crossover between sticky rate (log T)^{k-1} and wild rate T^{beta k / n}.

Two rates cross when they are equal:
    (log T)^{k-1} = T^{beta k / n}
    (k-1) log log T = (beta k / n) log T

For fixed T, solve for k:
    k [(log log T) - (beta / n) log T] = log log T
    k* = log log T / [log log T - (beta/n) log T]

This is T-dependent, so no closed-form k* independent of T exists.

However, we can define a "regime-crossover" k* such that:
- for k < k*, the sticky rate (log T)^{k-1} dominates
- for k > k*, the wild rate T^{beta k/n} dominates

At the crossover the two exponents (in log-log scale) equal:
    (k*-1) log log T = (beta k* / n) log T
   → k*-1 = (beta k*/n) · (log T / log log T)

Let L := log T / log log T. Then
    k* - 1 = beta L k* / n
    k* (1 - beta L/n) = 1
    k* = 1 / (1 - beta L / n) = n / (n - beta L)

For our panel: T = 13 quarters (or 39 obs). Let's compute for a few T.
"""
import math

def kstar(T, beta, n=3):
    L = math.log(T) / math.log(math.log(T))
    return n / (n - beta * L)

# On panel: T can be either 13 (quarters) or 39 (venue-quarter obs) or 4746 (venue-days).
for T in [13, 39, 156, 1000, 4746]:
    print(f"\nT = {T}   log T = {math.log(T):.3f}   log log T = {math.log(math.log(T)):.3f}")
    for beta in [0.1, 0.2, 0.3, 0.4, 0.5, 0.7]:
        ks = kstar(T, beta, 3)
        print(f"  beta={beta:.2f}  k* = {ks:+.3f}   ceil={math.ceil(ks) if ks>0 else 'div'}")

# The paper's original (buggy) formula
print("\n--- ORIGINAL FORMULA k* = ceil((1-b)n / (1+b(m-1))) ---")
for beta in [0.1, 0.2, 0.3, 0.4, 0.5]:
    orig = (1-beta) * 3 / (1 + beta * 4)
    print(f"  beta={beta:.2f}  orig={orig:.3f}  ceil={math.ceil(orig)}")
