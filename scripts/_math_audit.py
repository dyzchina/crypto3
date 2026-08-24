"""
Hard math check:

M3: Verify α(k,n,m) = k-1 + m(n-k)/d formula
    where d = n(m-1)

    Question: how is this derived from dim V_{k,n} ≤ d - k(m-1)?

    Candidate derivation A: α = (k-1) + dim V_{k,n} / d
    Candidate derivation B: α = k-1 + m(n-k)/d directly (stated)
    Candidate derivation C: α = (k-1) + (d - dim)/d = (k-1) + k(m-1)/d

    Test at endpoints k=1, k=n with (n,m)=(3,5), d=12:

M4: Verify crossover k*(T,β,n) = n/(n − βL(T)) at T=13, β̂=0.86
"""
import math

n, m = 3, 5
d = n * (m - 1)  # = 12

def alpha_stated(k, n, m):
    """As stated in Thm 1: α = k-1 + m(n-k)/d"""
    d = n * (m-1)
    return (k-1) + m*(n-k)/d

def alpha_from_dim(k, n, m):
    """If α = (k-1) + dim V / d, and dim V = d - k(m-1)"""
    d = n * (m-1)
    dim = d - k * (m-1)
    return (k-1) + dim/d

def alpha_from_codim(k, n, m):
    """If α = (k-1) + codim V / d = (k-1) + k(m-1)/d"""
    d = n * (m-1)
    return (k-1) + k*(m-1)/d

print(f"n={n}, m={m}, d={d}")
print()
print(f"{'k':>3s} {'stated':>10s} {'from_dim':>10s} {'from_codim':>12s}")
for k in [1, 2, 3]:
    print(f"{k:>3d} {alpha_stated(k,n,m):>10.4f} {alpha_from_dim(k,n,m):>10.4f} {alpha_from_codim(k,n,m):>12.4f}")

print()
print("Endpoint targets from Prop 1:")
print(f"  k=n=3: α should = n-1 = 2")
print(f"  k=1:   α should reduce to single-venue rate")
print()

# What actually recovers α(n,n,m) = n-1?
# alpha_stated(3,3,5) = 2 + 5·0/12 = 2 ✓
# alpha_from_dim(3,3,5) = 2 + (12-12)/12 = 2 ✓ (matches at k=n)
# alpha_from_codim(3,3,5) = 2 + 3·4/12 = 2 + 1 = 3 ✗

# So the "stated" form matches endpoint k=n; but at k=1:
# alpha_stated(1,3,5) = 0 + 5·2/12 = 10/12 = 5/6
# alpha_from_dim(1,3,5) = 0 + (12-4)/12 = 8/12 = 2/3

# Which is the correct derivation? Let's check if the stated formula
# CAN be derived from a different (fixed) dimension bound.
# The App A.2 stated: N_k ~ (log T)^{dim V_{k,n} / d}
# If dim V_{k,n} = m(n-k), then dim/d = m(n-k)/d
# At k=n: dim/d = 0, plus (k-1) = n-1 = 2 ✓
# At k=1: dim/d = m(n-1)/d, plus 0 = m(n-1)/d = 5·2/12 = 5/6 ✓
# So the correct dimension bound should be:
#     dim V_{k,n} ≤ m(n-k)
# Not:
#     dim V_{k,n} ≤ d - k(m-1)
#
# Let's check: at k=1, dim V_{1,n} = m(n-1) = 5·2 = 10
# But V_{1,n} is 1-fold distress region = union over one venue of D_e × rest
# rest is (n-1)·m ambient dim before row-sum constraints = 10 (for n=3,m=5)
# BUT with row-sum constraints on remaining venues: (n-1)(m-1) = 8
# So dim V_{1,n} = 10 or 8 depending on where the (m-1) applies.
#
# The paper's Prop 1 dim bound "d - k(m-1)" uses d = n(m-1) ambient dim
# and codim = k(m-1) constraints per venue.
# In this scheme, dim V_{k,n} = d - k(m-1) = 12 - 4 = 8 at k=1.
# Then dim/d = 8/12 = 2/3, not 5/6.
#
# So there IS an inconsistency between Prop 1 dimension bound (d - k(m-1))
# and Thm 1 exponent formula (k-1 + m(n-k)/d) at the k=1 endpoint.
# To reconcile, EITHER Prop 1 should read "dim V_{k,n} ≤ m(n-k)"
# OR Thm 1 exponent should read "α = k-1 + (d - k(m-1))/d = k(n-1)/n · [WRONG endpoint]"

print("=== Conclusion ===")
print(f"stated α at endpoints: k=1 → 5/6, k=n → 2")
print(f"derived α (from dim=d-k(m-1)): k=1 → 2/3, k=n → 2")
print(f"MISMATCH at k=1: 5/6 vs 2/3")
print()
print("Fix option A: change Prop 1 dim bound to dim V_{k,n} ≤ m(n-k)")
print("Fix option B: change Thm 1 exponent to α = k-1 + (d-k(m-1))/d")
print("             = k-1 + 1 - k(m-1)/d")
print("             = k - k(m-1)/(n(m-1))")
print("             = k(1 - 1/n) = k(n-1)/n")
print()
print("Testing option B at endpoints:")
for k in [1, 2, 3]:
    alt = k * (n-1) / n
    print(f"  k={k}: k(n-1)/n = {alt:.4f}")
print("  k=n=3: gives 3·2/3 = 2 ✓")
print("  k=1: gives 1·2/3 = 2/3, but paper says 5/6")
print()

# M4: crossover value at real β estimates
print("=== M4: Crossover k*(T,β,n) verification ===")
T = 13
L = math.log(T) / math.log(math.log(T))
print(f"T = {T},  L(T) = {L:.3f}")
print()
for beta in [0.30, 0.44, 0.50, 0.86, 1.28]:
    denom = n - beta * L
    kstar = n / denom if denom > 0 else float("inf")
    print(f"  β = {beta:.2f}: k*(T,β,n) = {n}/({n} - {beta}·{L:.3f}) = {n}/{denom:.3f} = {kstar:+.3f}")

print()
print("Paper claim: β̂=0.86 gives k* ≈ 4.5 → ⌈k*⌉=5 > n=3 (wild regime dominates)")
print("Paper claim: β lower bound 0.44 gives k* ≈ 1.67 → ⌈k*⌉=2 (agrees with empirical k̂*=2)")
